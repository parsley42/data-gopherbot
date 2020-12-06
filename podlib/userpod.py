from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
from podlib.config import get_config

def pod_types(project=""):
    """ Generates a string array of user pod types

    Parameters
    ----------
    project: str
        The name of the project, for project-specific types

    Returns
    -------
    types: str[]
        An array of pod types
    """

    cfg = get_config()
    # config.load_incluster_config()
    v1 = client.CoreV1Api()
    namespace = cfg["NAMESPACE"]

    type_maps = v1.list_namespaced_config_map(namespace, label_selector="class=userpod")
    types = []
    ntypes = len(type_maps.items)
    for i in range(ntypes):
        types.append(type_maps.items[i].metadata.name)
    return types

def userpod(pod_type, username, uid, groupname, gid, annotations={}):
    """Starts a user pod

    Parameters
    ----------
    pod_type: str
        The workload type of the pod to launch, e.g. "theia-python"
    user: str
        The username for the home directory, "user" or "user@dom"
    uid: int
        The numeric user ID of the user that the pod will run as
    groupname: str
        Opaque group name for project mount
    gid: int
        The numeric group ID the pod will run as
    annotations: dict
        Any additional annotations for the ingress

    Returns
    -------
    pod_dns: str
        The partly-random domain name of the pos; can be used to check
        the pod's status, and determines the URL: https://<pod_dns>
    """

    cfg = get_config()
    v1 = client.CoreV1Api()
    v1beta = client.ExtensionsV1beta1Api()
    namespace = cfg["NAMESPACE"]

    type_maps = v1.list_namespaced_config_map(namespace, label_selector="class=userpod")
    ntypes = len(type_maps.items)
    podcfg = None
    for i in range(ntypes):
        if type_maps.items[i].metadata.name == pod_type:
            podcfg = type_maps.items[i]
            break
    if not podcfg:
        raise Exception("Unsupported type")

    poddata = podcfg.data

    passwd = poddata["passwd"]
    passwd = passwd.replace("<UID>", str(uid))
    passwd = passwd.replace("<GID>", str(gid))
    group = poddata["group"]
    group = group.replace("<GID>", str(gid))
    podmap = {
        "passwd": passwd,
        "group": group,
    }
    dotted_username = username.replace("@", ".")
    dashed_username = username.replace("@", "-")
    dashed_username = dashed_username.replace(".", "-")

    cfgmap = client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        metadata=client.V1ObjectMeta(
            generate_name="%s-%s-" % (pod_type, dashed_username),
            labels={
                "dotted-username": dotted_username,
            },
        ),
        data=podmap,
    )
    created_map = v1.create_namespaced_config_map(namespace, cfgmap)

    pod_name = created_map.metadata.name
    patch_labels = {
        "user-pod": pod_name,
    }
    label = {
        "metadata": {
            "labels": patch_labels,
        },
    }
    v1.patch_namespaced_config_map(pod_name, namespace=namespace, body=label)

    resource_labels = {
        "dotted-username": dotted_username,
        "user-pod": pod_name,
    }

    pod_volumes = [
        client.V1Volume(
            name="passgrp",
            config_map=client.V1ConfigMapVolumeSource(
                name=pod_name,
            )
        ),
    ]

    pod_mounts = [
        client.V1VolumeMount(
            name="passgrp",
            mount_path="/etc/passwd",
            sub_path="passwd",
        ),
        client.V1VolumeMount(
            name="passgrp",
            mount_path="/etc/group",
            sub_path="group",
        ),
    ]

    if "HOME_PREFIX" in cfg:
        # NOTE / TODO: This will change eventually
        pod_volumes.append(
            client.V1Volume(
                name="home",
                host_path=client.V1HostPathVolumeSource(
                    path = "%s/%s" % (cfg["HOME_PREFIX"], username),
                    type = "Directory"
                )
            )
        )
        pod_mounts.append(
            client.V1VolumeMount(
                name="home",
                mount_path="/home/homedir"
            )
        )
    if "PROJECT_PREFIX" in cfg:
        pod_volumes.append(
            client.V1Volume(
                name="project",
                host_path=client.V1HostPathVolumeSource(
                    path = "%s/%s" % (cfg["PROJECT_PREFIX"], groupname),
                    type = "Directory"
                )
            )
        )
        pod_mounts.append(
            client.V1VolumeMount(
                name="project",
                mount_path="/home/project"
            )
        )

    registry = cfg["REGISTRY"]
    reg_org = cfg["REGISTRY_ORG"]

    pod = client.V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels=resource_labels,
        ),
        spec=client.V1PodSpec(
            volumes=pod_volumes,
            containers=[
                client.V1Container(
                    name=pod_type,
                    image="%s/%s/%s:latest" % (registry, reg_org, pod_type),
                    security_context=client.V1SecurityContext(
                        run_as_user=uid,
                        run_as_group=gid,
                    ),
                    volume_mounts=pod_mounts,
                )
            ],
        )
    )
    v1.create_namespaced_pod(namespace=namespace, body=pod)

    pod_port = int(poddata["port"])

    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels=resource_labels,
            namespace=namespace,
        ),
        spec=client.V1ServiceSpec(
            selector=resource_labels,
            ports=[client.V1ServicePort(
                port=80,
                protocol="TCP",
                target_port=pod_port,
            )]
        )
    )
    v1.create_namespaced_service(namespace, body=service)

    pod_dom = cfg["POD_DOMAIN"]
    pod_dns = "%s.%s" % (pod_name, pod_dom)

    annotations["kubernetes.io/ingress.class"] = "nginx"

    ingress = client.ExtensionsV1beta1Ingress(
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels=resource_labels,
            namespace=namespace,
            annotations=annotations,
        ),
        spec=client.ExtensionsV1beta1IngressSpec(
            rules=[client.ExtensionsV1beta1IngressRule(
                host=pod_dns,
                http=client.ExtensionsV1beta1HTTPIngressRuleValue(
                    paths=[client.ExtensionsV1beta1HTTPIngressPath(
                        path="/",
                        backend=client.ExtensionsV1beta1IngressBackend(
                            service_name=pod_name,
                            service_port=80,
                        ),
                    )],
                ),
            )],
        ),
    )
    v1beta.create_namespaced_ingress(namespace, body=ingress)

    return pod_dns

def podstatus(pod_dns):
    """ Checks the status of a user pod

    Parameters
    ----------
    pod_dns: str
        The dns name of the pod to check.

    Returns
    -------
    pod_status: str
        "Ready", "Pending", or "Error: <reason>"
    """

    cfg = get_config()
    # config.load_incluster_config()
    v1 = client.CoreV1Api()
    namespace = cfg["NAMESPACE"]

    name_components = pod_dns.split(".")
    pod_name = name_components[0]

    try:
        pstat = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            return "Error: Pod not found"
        else:
            return "Error: %s" %e

    status = pstat.status.phase

    if status == "Running":
        return "Ready"
    elif status == "Pending":
        return "Pending"
    elif status == "Succeeded":
        return "Error: All containers exited (successfully)"
    elif status == "Failed":
        return "Error: All containers existed, at least one failed"
    elif status == "Unknown":
        return "Error: Pod status could not be determined"

def userpods(username):
    """Returns a list of pod dns entries for a user

    Parameters
    ----------
    username: str
        The full username, e.g. "<user>" or "<user>@<some.dom>"

    Returns
    -------
    pod_dns: []str
        An array of user pod dns names
    """

    cfg = get_config()
    v1 = client.CoreV1Api()
    namespace = cfg["NAMESPACE"]
    pod_dom = cfg["POD_DOMAIN"]

    dotted_username = username.replace("@", ".")
    selector = "dotted-username=%s" % dotted_username

    pod_dns=[]
    pods = v1.list_namespaced_pod(namespace, label_selector=selector)
    for pod in pods.items:
        pod_full = "%s.%s" % (pod.metadata.name, pod_dom)
        pod_dns.append(pod_full)

    return pod_dns

def terminate(pod_dns):
    """Terminates a user pod, and removes the service and ingress

    Parameters
    ----------
    pod_dns: str
        The full dns name of the pod to terminate
    """

    cfg = get_config()
    v1 = client.CoreV1Api()
    v1beta = client.ExtensionsV1beta1Api()
    namespace = cfg["NAMESPACE"]

    name_components = pod_dns.split(".")
    pod_name = name_components[0]

    v1.delete_namespaced_pod(pod_name, namespace)
    v1.delete_namespaced_service(pod_name, namespace)
    v1beta.delete_namespaced_ingress(pod_name, namespace)
