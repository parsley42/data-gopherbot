from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

def get_config():
    """ Consults the environment for namespace and configmap name
    to load for configuration.

    Returns
    -------
    config: dict{}
        A dictionary of key: values with userpod configuration
    """

    incluster = os.getenv("PODLIB_INCLUSTER")
    if incluster and incluster == "true":
        config.load_incluster_config()
    else:
        config.load_kube_config()
    v1 = client.CoreV1Api()

    namespace = os.getenv("PODLIB_NAMESPACE")
    if not namespace:
        raise Exception("PODLIB_NAMESPACE not set in the environment")
    cfgmap = os.getenv("PODLIB_CONFIG")
    if not cfgmap:
        raise Exception("PODLIB_CONFIG not set in the environment")

    cmap = v1.read_namespaced_config_map(cfgmap, namespace)
    data = cmap.data
    data["NAMESPACE"] = namespace
    return data
