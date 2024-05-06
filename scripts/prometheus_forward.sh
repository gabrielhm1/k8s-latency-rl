#! /bin/bash

while true; do
    kubectl port-forward svc/prometheus 9090:9090 -n istio-system
done