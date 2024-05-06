from prometheus_api_client import PrometheusConnect
from logging import getLogger

logger = getLogger("model_logger")

URL = "http://localhost:9090"


def run_prometheus_query(query):
    # Connect to Prometheus instance
    prom = PrometheusConnect(url=URL)

    result = prom.custom_query(query)

    return result


def create_graph(service_name, namespace="onlineboutique"):
    graph_node = {"destination": [], "source": []}

    source_query = (
        'sum(istio_requests_total{namespace="'
        + namespace
        + '", reporter="source", destination_service_name="'
        + service_name
        + '"}) by (source_app, destination_app)'
    )
    destination_query = (
        'sum(istio_requests_total{namespace="'
        + namespace
        + '", reporter="source", source_app="'
        + service_name
        + '"}) by (source_app, destination_app)'
    )
    source_response = run_prometheus_query(source_query)
    destination_response = run_prometheus_query(destination_query)

    for node in destination_response:
        graph_node["destination"].append(node["metric"]["destination_app"])
    for node in source_response:
        graph_node["source"].append(node["metric"]["source_app"])

    return graph_node


def get_metrics(app_graph, service_name, namespace):
    app_metrics = {}
    print("Initial get_metrics")

    try:
        app_graph["destination"].remove("unknown")
    except:
        pass

    # destination_metrics = {
    #     "request_size_p50": "istio_request_bytes_bucket",
    #     "latency_p50": "istio_request_duration_milliseconds_bucket",
    # }
    destination_metrics = {
        "avg_request_size": ["istio_request_bytes_sum", "istio_request_bytes_count"],
        "avg_request_duration": [
            "istio_request_duration_milliseconds_sum",
            "istio_request_duration_milliseconds_count",
        ],
    }

    for app in app_graph["destination"]:
        app_metrics[app] = {}
        for k, v in destination_metrics.items():
            # 50 percentile
            # metric = (
            #     '(histogram_quantile(0.50, sum(irate(%s{reporter=~"source", destination_service_name=~"%s", source_app=~"%s"}[5m])) by (source_app, destination_service_name, le))) '
            #     % (v, app, service_name)
            # )

            # avg
            metric = (
                'round(sum(increase(%s{namespace="%s", reporter=~"source", destination_service_name=~"%s", source_app=~"%s"}[5m])) by (source_app, destination_service_name) / sum (increase(%s{namespace="%s", reporter=~"source", destination_service_name=~"%s", source_app=~"%s"}[5m])) by (source_app, destination_service_name))'
                % (
                    v[0],
                    namespace,
                    app,
                    service_name,
                    v[1],
                    namespace,
                    app,
                    service_name,
                )
            )

            query_response = run_prometheus_query(metric)

            try:
                app_metrics[app][k] = (
                    int(query_response[0].get("value", 0)[1]) if query_response else 0
                )
            except Exception as e:
                app_metrics[app][k] = 0
                logger.error(f"Error: {e} to set metrics {k} for {app}")

    for app in app_graph["source"]:
        for k, v in destination_metrics.items():
            # 50 percentile
            # metric = (
            #     '(histogram_quantile(0.50, sum(irate(%s{reporter=~"source", destination_service_name=~"%s", source_app=~"%s"}[5m])) by (source_app, destination_service_name, le))) '
            #     % (v, service_name, app)
            # )

            # avg metric
            metric = (
                'round(sum(increase(%s{namespace="%s", reporter=~"source", destination_service_name=~"%s", source_app=~"%s"}[5m])) by (source_app, destination_service_name) / sum(increase(%s{namespace="%s", reporter=~"source", destination_service_name=~"%s", source_app=~"%s"}[5m])) by (source_app, destination_service_name))'
                % (
                    v[0],
                    namespace,
                    service_name,
                    app,
                    v[1],
                    namespace,
                    service_name,
                    app,
                )
            )
            query_response = run_prometheus_query(metric)

            if app not in app_metrics:
                app_metrics[app] = {}

            try:
                app_metrics[app][k] = (
                    int(query_response[0].get("value", 0)[1]) if query_response else 0
                )
            except Exception as e:
                app_metrics[app][k] = 0
                logger.error(f"Error: {e} to set metrics {k} for {app}")

    return app_metrics


def get_application_latency(namespace):
    latency_query = (
        'round(sum(increase(istio_request_duration_milliseconds_sum{reporter="source", source_app="loadgenerator", destination_app="frontend", namespace="'
        + namespace
        + '"}[5m])) by (source_app, destination_app) / sum(increase(istio_request_duration_milliseconds_count{reporter="source", source_app="loadgenerator", destination_app="frontend", namespace="'
        + namespace
        + '"}[5m])) by (source_app, destination_app))'
    )
    response = run_prometheus_query(latency_query)
    try:
        return int(response[0].get("value", 0)[1])
    except Exception as e:
        logger.error(f"Error: {e} to get latency")
        return 0
    # except:
    #     return 0
