
def create_state_space(k8s_metrics, prom_metrics, service_name,node_list):
    app_services = [
        "frontend",
        "recommendationservice",
        "cartservice",
        "productcatalogservice",
        "adservice",
        "shippingservice",
        "checkoutservice",
        "emailservice",
        "paymentservice",
        "currencyservice",
    ]
    nodes = ["worker1", "worker2", "worker3"]
    state_space = []
    for app in app_services:
        pod_nodes = k8s_metrics.get(app, None)
        if app == service_name:
            state_space.extend(
                [
                    1,
                    pod_nodes.count(nodes[0]),
                    pod_nodes.count(nodes[1]),
                    pod_nodes.count(nodes[2]),
                    0,
                ]
            )
        elif pod_nodes is not None:
            state_space.extend(
                [
                    0,
                    pod_nodes.count(nodes[0]),
                    pod_nodes.count(nodes[1]),
                    pod_nodes.count(nodes[2]),
                    int(prom_metrics[app]),
                ]
            )
        else:
            state_space.extend([0, 0, 0, 0, 0])
    state_space.extend([v for v in node_list.values()])
    return state_space

def calculate_latency(ob):
    worker_latency = [5,4,7]
    app_services = [
        "frontend",
        "recommendationservice",
        "cartservice",
        "productcatalogservice",
        "adservice",
        "shippingservice",
        "checkoutservice",
        "emailservice",
        "paymentservice",
        "currencyservice",
    ]
    total_requests = 0
    app_weights = []
    mean_latency = 0
    service_index = 0
    for count,element in enumerate(app_services):
        if ob[(count*5)] == 1:
            service_index = count
        total_requests += ob[(count*5)+4]

    currently_app = service_index * 5
    currently_node_list = ob[currently_app + 1 : currently_app + 4]
    total_sum = 0
    total_weight = 0
    for app in app_services:
        parcial_sum = 0
        parcial_weight = 0
        if app == app_services[service_index]:
            continue
        app_index = app_services.index(app)
        start_index = app_index * 5
        neighbor_node_list = ob[start_index + 1 : start_index + 4]
        for i in range(3):
            if currently_node_list[i] <= 0:
                continue
            for j in range(3):
                if neighbor_node_list[j] > 0:
                    if i == j:
                        latency_weight = 0
                    else:
                        latency_weight = worker_latency[i] + worker_latency[j]                        
                    parcial_sum += currently_node_list[i] * neighbor_node_list[j] * latency_weight
                    parcial_weight += currently_node_list[i] * neighbor_node_list[j]
        total_sum += (parcial_sum * ob[(app_index * 5) + 4])
        total_weight += parcial_weight * ob[(app_index * 5) + 4]

    mean_latency = total_sum / total_weight if total_weight > 0 else 0
    return mean_latency