from os import getenv
from json import loads as json_loads
import random
import sys

from kubernetes import config, watch
from kubernetes.client import (
    ApiClient,
    CoreV1Api,
    V1ObjectReference,
    V1ObjectMeta,
    V1Binding,
    Configuration,
)
from kubernetes.client.rest import ApiException, RESTClientObject
import utils.prometheus_metrics as prometheus_metrics
from utils.action_space import create_state_space

from logging import getLogger


logger = getLogger("model_logger")

V1_CLIENT = None  # type: CoreV1Api
SCHEDULE_STRATEGY = "project=latency-network"
_NOSCHEDULE_TAINT = "NoSchedule"
config.load_kube_config()


def _get_ready_nodes(v1_client, filtered=True):
    ready_nodes = []
    try:
        for n in v1_client.list_node().items:
            if n.metadata.labels.get("noCustomScheduler") == "yes":
                logger.info(
                    f"Skipping Node {n.metadata.name} since it has noCustomScheduler label"
                )
                continue
            if filtered:
                if not n.spec.unschedulable:
                    no_schedule_taint = False
                    if n.spec.taints:
                        for taint in n.spec.taints:
                            if _NOSCHEDULE_TAINT == taint.to_dict().get("effect", None):
                                no_schedule_taint = True
                                break
                    if not no_schedule_taint:
                        for status in n.status.conditions:
                            if (
                                status.status == "True"
                                and status.type == "Ready"
                                and n.metadata.name
                            ):
                                ready_nodes.append(n.metadata.name)
                    else:
                        logger.error(
                            "NoSchedule taint effect on node %s", n.metadata.name
                        )
                else:
                    logger.error("Scheduling disabled on %s ", n.metadata.name)
            else:
                if n.metadata.name:
                    ready_nodes.append(n.metadata.name)
        logger.info("Nodes : %s, Filtered: %s", ready_nodes, filtered)
    except ApiException as e:
        logger.error(json_loads(e.body)["message"])
        ready_nodes = []
    return ready_nodes


def _get_schedulable_node(v1_client):
    node_list = _get_ready_nodes(v1_client)
    if not node_list:
        return None
    available_nodes = list(set(node_list))
    return random.choice(available_nodes)


def schedule_pod(pod_name, node, namespace="onlineboutique"):
    V1_CLIENT = CoreV1Api()
    target = V1ObjectReference(api_version="v1", kind="Node", name=node)
    meta = V1ObjectMeta(name=pod_name)
    body = V1Binding(
        api_version=None,
        kind=None,
        metadata=meta,
        target=target,
    )
    logger.info("Binding Pod: %s  to  Node: %s", pod_name, node)
    try:
        V1_CLIENT.create_namespaced_pod_binding(
            pod_name,
            namespace,
            body,
            _preload_content=False,
        )
    except Exception as e:
        logger.error("Pod {pod_name} failed to bind to Node {node} due to {e}")


def get_pod_node_list(v1_client, namespace, label_selector):
    response = {}
    pods_reponse = v1_client.list_namespaced_pod(
        namespace, label_selector=label_selector
    )
    for pod in pods_reponse.items:
        if pod.metadata.labels.get("app", None) is None:
            print(f"Pod {pod.metadata.name} has no app label")
            continue
        if pod.metadata.labels["app"] not in response:
            response[pod.metadata.labels["app"]] = [pod.spec.node_name]
        else:
            response[pod.metadata.labels["app"]].append(pod.spec.node_name)
    return response


def get_pod_info(pod_name, app_name, namespace="default"):
    V1_CLIENT = CoreV1Api()
    # logger.info(f"Pod Name: {pod_name}, App Name: {app_name}")
    logger.info("Collecting neighbor of %s", app_name)
    neighbor_app = prometheus_metrics.create_graph(app_name, namespace)
    logger.info(f"Neighbor: {neighbor_app}")
    app_string = app_name
    for app in neighbor_app["destination"]:
        app_string += "," + app
    for app in neighbor_app["source"]:
        app_string += "," + app
    neighbor_labels = f"app in ({app_string})"
    prom_metrics = prometheus_metrics.get_metrics(neighbor_app, app_name, namespace)

    logger.info(f"Getting Nodes")
    current_neighbor = get_pod_node_list(V1_CLIENT, namespace, neighbor_labels)

    logger.info(f"Creating State Space")
    state_space = create_state_space(current_neighbor, prom_metrics, app_name)

    return state_space


def scheduler_watcher(namespace, pod_scheduled=[]):
    V1_CLIENT = CoreV1Api()
    while True:
        logger.info("Checking for pod events....")
        try:
            watcher = watch.Watch()
            for event in watcher.stream(
                V1_CLIENT.list_namespaced_pod,
                namespace=namespace,
                label_selector=SCHEDULE_STRATEGY,
                timeout_seconds=20,
            ):
                if event["object"].status.phase == "Pending":
                    try:
                        pod_name = event["object"].metadata.name
                        if pod_name in pod_scheduled:
                            logger.debug(f"Pod {pod_name} already scheduled")
                            continue
                        logger.debug(
                            f"Event: {event['type']} {event['object'].kind}, {event['object'].metadata.namespace}, {event['object'].metadata.name}, {event['object'].status.phase}"
                        )
                        app_name = event["object"].metadata.labels["app"]
                        return {
                            "pod_name": pod_name,
                            "app_name": app_name,
                        }
                    except ApiException as e:
                        logger.error(json_loads(e.body)["message"])
            logger.debug("Resetting k8s watcher...")
        except Exception as e:
            logger.error("Error in watcher: %s", e)
        finally:
            del watcher


def main():
    logger.info("Initializing the meetup scheduler...")
    logger.info("Watching for pod events...")
    watch_pod_events()


if __name__ == "__main__":
    config.load_kube_config()
    main()
