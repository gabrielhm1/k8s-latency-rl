# self.Pods? 1 : 0 - 1, # Esse pod esta sendo alocado?
# qtd_replicas,  # Number of Pods  -- 1) recommendationservice - alocando
# 1,  # qtd na maquina 1
# 3,  # qtd na maquina 2
# 0,  # qtd na maquina 3
# 0,  # media da latencia
# 0,  # media bytes trocados


def create_state_space(k8s_metrics, service_name):
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
    nodes = ["worker-1", "worker-2", "worker-3"]
    state_space = []
    for app in app_services:
        pod_nodes = k8s_metrics.get(app, None)
        if app == service_name:
            state_space.extend(
                [
                    1,
                    len(pod_nodes),
                    pod_nodes.count(nodes[0]),
                    pod_nodes.count(nodes[1]),
                    pod_nodes.count(nodes[2]),
                ]
            )
        elif pod_nodes is not None:
            state_space.extend(
                [
                    0,
                    len(pod_nodes),
                    pod_nodes.count(nodes[0]),
                    pod_nodes.count(nodes[1]),
                    pod_nodes.count(nodes[2]),
                ]
            )
        else:
            state_space.extend([0, 0, 0, 0, 0])
    return state_space
