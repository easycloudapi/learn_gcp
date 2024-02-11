"""
Ref:
1. https://github.com/googleapis/google-api-python-client/blob/main/samples/compute/create_instance.py

```shell
source .venv/bin/activate
pip install --upgrade google-api-python-client

python python_discovery_create_gcp_vm.py
```

"""

import time
import googleapiclient.discovery

compute = googleapiclient.discovery.build("compute", "v1")


def create_instance(project, zone, name):
    # Get the latest Debian image.
    image_response = (
        compute.images()
        .getFromFamily(project="debian-cloud", family="debian-11")
        .execute()
    )
    source_disk_image = image_response["selfLink"]
    print(f"source_disk_image: {source_disk_image}")

    # machine type
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    print(f"machine_type: {machine_type}")

    config = {
        "name": name,
        "machineType": machine_type,
        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": source_disk_image,
                },
            }
        ],
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}],
            }
        ]
    }
    return compute.instances().insert(project=project, zone=zone, body=config).execute()

def delete_instance(project, zone, name):
    return (
        compute.instances().delete(project=project, zone=zone, instance=name).execute()
    )

def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result.get("items")

def wait_for_operation(project, zone, operation):
    print("Waiting for operation to finish...")
    while True:
        result = (
            compute.zoneOperations()
            .get(project=project, zone=zone, operation=operation)
            .execute()
        )

        if result["status"] == "DONE":
            print("done.")
            if "error" in result:
                raise Exception(result["error"])
            else:
                print("processing..")
            return result
        time.sleep(2)


if __name__ == "__main__":
    print("Creating instance.")

    project = "test-flask-api-372913"
    zone = "us-central1-f"
    instance_name = "demo-sample-vm-001"
    operation = create_instance(project, zone, instance_name)
    wait_for_operation(project, zone, operation["name"])