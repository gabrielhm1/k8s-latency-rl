import random



APPS = [
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

class OfflineEnv():
    def __init__(self, **kwargs):
        self.apps_distribution = {
        }
        self.nodes_distribution = [0, 0, 0]
        for app in APPS:
            self.apps_distribution[app] = [0, 0, 0]
            selected_node = random.randint(0, 2)
            self.apps_distribution[app][selected_node] = 1
            self.nodes_distribution[selected_node] += 1
        self.workers = ["worker1", "worker2", "worker3"]
    
    def add_pod(self, app, node=None):
        if node is None:
            node = random.randint(0, 2)

        self.apps_distribution[app][node] += 1
        self.nodes_distribution[node] += 1
    
    def remove_pod(self, app, node=None):
        if node is None:
            node_available = [i for i, e in enumerate(self.apps_distribution[app]) if e > 0]
            node = random.choice(node_available)
        self.apps_distribution[app][node] -= 1
        self.nodes_distribution[node] -= 1

    def scale(self, app, replicas):
        current_replicas = sum(self.apps_distribution[app])
        if current_replicas < replicas:
            for i in range(replicas - current_replicas):
                node = random.randint(0, 2)
                self.add_pod(app, node)
        elif current_replicas > replicas:
            for i in range(current_replicas - replicas):
                node = random.randint(0, 2)
                self.remove_pod(app)
    
    def get_app(self, app):
        return self.apps_distribution[app]
    def get_node(self, node):
        return self.nodes_distribution[node]
    def get_nodes(self):
        node_json = {}
        for i in range(len(self.workers)):
            node_json[self.workers[i]] = self.nodes_distribution[i]
        print(node_json)

        return node_json
    def get_apps_node(self,apps):
        apps_nodes = {}
        for app in apps:
            for i,node_count in enumerate(self.apps_distribution.get(app, [0])):
                if node_count > 0:
                    if app not in apps_nodes:
                        apps_nodes[app] = [self.workers[i]]*node_count
                    else:
                        apps_nodes[app].extend([self.workers[i]]*node_count)
        return apps_nodes
    def allocate_pod(self):
        pod = random.choice(APPS)
        response = {
                            "pod_name": f"{pod}-pod-{random.randint(1, 1000)}",
                            "app_name": pod,
                        }
        return response
        

