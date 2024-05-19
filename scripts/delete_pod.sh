MIN_PODS=10
index=0


while [ true ]; do
    for i in {1..10}; do
        # Store the result of the kubectl command in a variable
        array_size=0
        while [ "$array_size" -lt $MIN_PODS ]; do
            result=$(kubectl get pod -n learning -l project=latency-network -o jsonpath='{.items[*].metadata.name}' --field-selector=status.phase='Running')

            # Split the result into an array using newline as the delimiter
            IFS=$' ' read -r -a pod_names <<< "$result"

            # Check the size of the array
            array_size=${#pod_names[@]}
            sleep 3
        done
        # Check if the array is not empty
        if [ "$array_size" -gt 0 ]; then
            # Generate a random number within the array size range
            random_index=$(( RANDOM % array_size ))

            # Select a random pod name from the array
            selected_pod="${pod_names[random_index]}"
            sleep 7

            # Delete the selected pod
            echo "Deleting pod: $selected_pod"
            kubectl delete pod "$selected_pod" -n learning
        else
            echo "No pods found in the array."
        fi
    done
    sleep 65
done
