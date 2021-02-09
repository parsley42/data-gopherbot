from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
import base64
from podlib.config import get_config

def userfence(username):
    """Disconnects a user from any owned pods

    Parameters
    ----------
    username: str
        The full username, e.g. "mst3k"

    Returns
    -------
    pods: int
        The number of fenced pods
    """

    # TODO: how do we prevent the user from creating new pods?
