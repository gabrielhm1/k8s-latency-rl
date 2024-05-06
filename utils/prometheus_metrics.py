from prometheus_api_client import PrometheusConnect

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
        + '"}) by (source_workload, destination_workload)'
    )
    destination_query = (
        'sum(istio_requests_total{namespace="'
        + namespace
        + '", reporter="source", source_workload="'
        + service_name
        + '"}) by (source_workload, destination_workload)'
    )
    source_response = run_prometheus_query(source_query)
    destination_response = run_prometheus_query(destination_query)

    for node in destination_response:
        graph_node["destination"].append(node["metric"]["destination_workload"])
    for node in source_response:
        graph_node["source"].append(node["metric"]["source_workload"])

    return graph_node


def get_metrics(app_graph, service_name):
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
            #     '(histogram_quantile(0.50, sum(irate(%s{reporter=~"source", destination_service_name=~"%s", source_workload=~"%s", source_workload_namespace=~"onlineboutique"}[5m])) by (source_workload, destination_service_name, le))) '
            #     % (v, app, service_name)
            # )

            # avg
            metric = (
                'sum(increase(%s{namespace="onlineboutique", reporter=~"source", destination_service_name=~"%s", source_workload=~"%s", source_workload_namespace=~"onlineboutique"}[5m])) by (source_workload, destination_service_name) / sum (increase(%s{namespace="onlineboutique", reporter=~"source", destination_service_name=~"%s", source_workload=~"%s", source_workload_namespace=~"onlineboutique"}[5m])) by (source_workload, destination_service_name)'
                % (v[0], app, service_name, v[1], app, service_name)
            )

            query_response = run_prometheus_query(metric)
            app_metrics[app][k] = query_response[0].get("value", 0)[1]

    for app in app_graph["source"]:
        for k, v in destination_metrics.items():
            # 50 percentile
            # metric = (
            #     '(histogram_quantile(0.50, sum(irate(%s{reporter=~"source", destination_service_name=~"%s", source_workload=~"%s", source_workload_namespace=~"onlineboutique"}[5m])) by (source_workload, destination_service_name, le))) '
            #     % (v, service_name, app)
            # )

            # avg metric
            metric = (
                'sum(increase(%s{namespace="onlineboutique", reporter=~"source", destination_service_name=~"%s", source_workload=~"%s", source_workload_namespace=~"onlineboutique"}[5m])) by (source_workload, destination_service_name) / sum(increase(%s{namespace="onlineboutique", reporter=~"source", destination_service_name=~"%s", source_workload=~"%s", source_workload_namespace=~"onlineboutique"}[5m])) by (source_workload, destination_service_name)'
                % (v[0], service_name, app, v[1], service_name, app)
            )
            query_response = run_prometheus_query(metric)

            if app not in app_metrics:
                app_metrics[app] = {}
                app_metrics[app][k] = query_response[0].get("value", 0)[1]
            else:
                app_metrics[app][k] = (
                    float(app_metrics[app].get(k, 0))
                    + float(query_response[0].get("value", 0)[1])
                ) / 2

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
    print(f"Latency: {response}")

    return int(response[0].get("value", 0)[1])
    # except:
    #     return 0
