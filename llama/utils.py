from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute

ml_client = MLClient.from_config()

def ensure_compute_exists(name: str):
    try:
        ml_client.compute.get(name)
        print(f"Compute '{name}' already exists.")
    except:
        print(f"Creating compute: {name}")
        cluster = AmlCompute(
            name=name,
            size="Standard_NC6",  # GPU-enabled
            min_instances=0,
            max_instances=1,
            idle_time_before_scale_down=120
        )
        poller = ml_client.begin_create_or_update(compute_cluster)
        poller.result()
        print(f"Compute target '{name}' created.")        
