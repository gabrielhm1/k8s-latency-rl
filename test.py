

node = ["worker1", "worker2", "worker3"]
counts = [4, 3, 2]

node_ar = []
for i,e in enumerate(counts):
    node_ar.extend([node[i]]*e)

print(node_ar)
temp = [node[i]]*10
print(temp)