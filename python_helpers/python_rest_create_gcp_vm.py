"""
Ref:
1. https://cloud.google.com/compute/docs/reference/rest/v1/instances/insert
2. https://cloud.google.com/compute/docs/instances/create-start-instance

python python_rest_create_gcp_vm.py
"""

import uuid
import json
import requests
import google.auth
from google.auth.transport.requests import AuthorizedSession

credentials, project = google.auth.default()
authed_session = AuthorizedSession(credentials)


def create_vm_using_rest(project, zone):
    base_url = f'https://compute.googleapis.com/compute/v1/projects/{project}/zones/{zone}/instances'
    
    headers =  {
        "Content-Type": "application/json"
    }
    
    data = {
      "disks": [
        {
          "autoDelete": "true",
          "boot": "true",
          "initializeParams": {
            "sourceImage": "projects/debian-cloud/global/images/family/debian-11"
          },
          "mode": "READ_WRITE",
          "type": "PERSISTENT"
        },
        # {
        #   "autoDelete": "false",
        #   "boot": "false",
        #   "mode": "READ_WRITE",
        #   "source": f"zones/{zone}/disks/my-override-disk",
        #   "type": "PERSISTENT"
        # }
      ],
      "networkInterfaces":[
        {
            "network":"global/networks/default"
        }
        ],
      "machineType": f"zones/{zone}/machineTypes/e2-standard-2",
      "name": "example-instance"
    }

    response = authed_session.post(url=base_url, data=json.dumps(data), headers=headers)
    print(f"response.status_code: {response.status_code}")
    return response.json()


def get_vm(project="debian-cloud"):
    base_url = f"https://compute.googleapis.com/compute/v1/projects/{project}/global/images/"

    headers =  {
        "Content-Type": "application/json"
    }
    out = {}
    try:
        response = authed_session.get(url=base_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Project: {project} can't be accessed")
        else:
            images = response.json()
            for item in images["items"]:
                print(f"item: {item['name']}")
    except Exception as e:
        print(f"error occured, {e}")
    return out


if __name__  == "__main__":
    out = create_vm_using_rest(project="test-flask-api-372913", zone="us-central1-c")
    print(f"out: {out}")

    # out = get_vm(project="debian-cloud")
    # print(f"out: {out}")