#! /bin/bash


while [ true ]; do
    array_size=0
    result=$(kubectl get pod -n learning -l project=latency-network -o jsonpath='{.items[*].metadata.name}' --field-selector=status.phase='Running')

    IFS=$' ' read -r -a pod_names <<< "$result"

    array_size=${#pod_names[@]}
    if [ "$array_size" -gt 0 ]; then
        # Generate a random number within the array size range
        random_index=$(( RANDOM % array_size ))

        # Select a random pod name from the array
        selected_pod="${pod_names[random_index]}"
        # Delete the selected pod
        echo "Deleting pod: $selected_pod"
        kubectl delete pod "$selected_pod" -n learning
        return 0
    else
        echo "No pods found in the array."
    fi
done
