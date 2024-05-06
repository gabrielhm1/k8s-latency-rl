import numpy as np

high = np.array(
    [
        1,  # Current Pod  -- 1) recommendationservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 2) productcatalogservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 3) cartservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 4) adservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 5) paymentservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 6) shippingservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 7) currencyservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 9) checkoutservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 10) frontend
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
        1,  # Current Pod -- 11) emailservice
        10,  # Desired Replicas
        10,  # Pod on Worker-1
        10,  # Pod on Worker-2
        10,  # Pod on Worker-3
    ]
)

# Define the shape of the multi-dimensional array
shape = (10, 10, 10, 3)  # 2 services, 10 replicas, 10 pods per worker, 10 workers

# Convert multi-dimensional indices to flat index
flat_index = np.ravel_multi_index(high, shape)
print("Flat index:", flat_index)
