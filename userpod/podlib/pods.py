from kubernetes import client, config
from kubernetes.client.rest import ApiException
import podlib.passgrp as passgrp
import os

pod_dom = os.getenv("USERPOD_DOM")
registry = os.getenv("USERPOD_REGISTRY")
registry_org = os.getenv("USERPOD_REGISTRY_ORG")

def get_config():
    """ Consults the environment for namespace and configmap name
    to load for configuration.

    Returns
    -------
    config: dict{}
        A dictionary of key: values with userpod configuration
    """

    config.load_incluster_config()
    v1 = client.CoreV1Api()

    namespace = os.getenv("USERPOD_NAMESPACE")
    cfgmap = os.getenv("USERPOD_CONFIG")

    cmap = v1.read_namespaced_config_map(cfgmap, namespace)
    data = cmap.data
    data["NAMESPACE"] = namespace
    return data

def podtypes():
    """ Generates a string array of user pod types

    Returns
    -------
    types: str[]
        An array of pod types.
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

def podstatus(pod_name):
    """ Checks the status of a user pod

    Parameters
    ----------
    pod_name: str
        The name of the pod to check.

    Returns
    -------
    pod_status: str
        "Ready", "Pending", or "Error: <reason>"
    """

    config.load_incluster_config()
    v1 = client.CoreV1Api()

    try:
        pstat = v1.read_namespaced_pod(name=pod_name, namespace="accord")
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

def userpod(pod_type, username, uid, groupname, gid):
    """Starts a user pod

    Parameters
    ----------
    pod_type : str
        The workload type of the pod to launch, e.g. "theia-python"
    eppn: str
        The EduPerson Principal Name of the user
    uid: int
        The numeric user ID of the user that the pod will run as
    groupname: str
        Opaque group name for project mount
    gid: int
        The numeric group ID the pod will run as

    Returns
    -------
    pod_name: str
        The partly-random string name of the pod; can be used to check
        the pod's status, and when combined with the domain name determines
        the URL: https://<pod-name>.<domain>
    """

    if pod_type != "theia-python":
        raise Exception("Unsupported type")
    username = eppn.split("@")[0]

    config.load_incluster_config()
    v1 = client.CoreV1Api()
    v1beta = client.ExtensionsV1beta1Api()

    cfgmap = client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        metadata=client.V1ObjectMeta(
            generate_name="%s-%s-" % (pod_type, username),
            labels={
                "dotted-eppn": eppn.replace("@", "."),
            },
        ),
        data=passgrp.pass_grp(pod_type, username, uid, gid)
    )
    created_map = v1.create_namespaced_config_map("accord", cfgmap)

    pod_name = created_map.metadata.name
    patch_labels = {
        "user-pod": pod_name,
    }
    label = {
        "metadata": {
            "labels": patch_labels,
        },
    }
    v1.patch_namespaced_config_map(pod_name, namespace="accord", body=label)

    resource_labels = {
        "dotted-eppn": eppn.replace("@", "."),
        "user-pod": pod_name,
    }

    pod = client.V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels=resource_labels,
        ),
        spec=client.V1PodSpec(
            volumes=[
                client.V1Volume(
                    name="home",
                    empty_dir=client.V1EmptyDirVolumeSource(),
                ),
                client.V1Volume(
                    name="project",
                    empty_dir=client.V1EmptyDirVolumeSource(),
                ),
                client.V1Volume(
                    name="passgrp",
                    config_map=client.V1ConfigMapVolumeSource(
                        name=pod_name,
                    )
                ),
            ],
            containers=[
                client.V1Container(
                    name=pod_type,
                    image="%s/accord/%s:latest" % (registry, pod_type),
                    command=[
                        "node",
                        "/home/theia/src-gen/backend/main.js",
                        "/home",
                        "--hostname=0.0.0.0",
                    ],
                    security_context=client.V1SecurityContext(
                        run_as_user=uid,
                        run_as_group=gid,
                    ),
                    volume_mounts=[
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
                        client.V1VolumeMount(
                            name="home",
                            mount_path="/home/%s" % username,
                        ),
                        client.V1VolumeMount(
                            name="project",
                            mount_path="/home/project",
                        ),
                    ],
                )
            ],
        )
    )
    v1.create_namespaced_pod(namespace="accord", body=pod)

    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels=resource_labels,
            namespace="accord",
        ),
        spec=client.V1ServiceSpec(
            selector=resource_labels,
            ports=[client.V1ServicePort(
                port=80,
                protocol="TCP",
                target_port=3000,
            )]
        )
    )
    v1.create_namespaced_service("accord", body=service)

    ingress = client.ExtensionsV1beta1Ingress(
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels=resource_labels,
            namespace="accord",
        ),
        spec=client.ExtensionsV1beta1IngressSpec(
            rules=[client.ExtensionsV1beta1IngressRule(
                host="%s.%s" % (pod_name, pod_dom),
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
    v1beta.create_namespaced_ingress("accord", body=ingress)

    return pod_name
