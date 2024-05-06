#! /bin/bash

kubectl taint nodes foo project=iar-tp1:NoSchedule
kubectl drain worker-1 --ignore-daemonsets
k uncordon worker-1
k apply -f boutique_app.yml
k label node worker-1 project="iar-tp1"