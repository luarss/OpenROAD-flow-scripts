# Ray Cluster Setup on Google Cloud Platform (GCP)

This tutorial covers the setup of Ray Clusters on GCP. Ray Clusters are a way to
start compute intensive jobs (e.g. Autotuner) on a distributed set of nodes spawned 
automatically. For more information on Ray Cluster, refer to [here](https://docs.ray.io/en/latest/cluster/getting-started.html).

To run Autotuner jobs on Ray Cluster, we have to first install ORFS onto the
GCP nodes.

There are two different ways for ORFS setup on Ray Cluster, namely:
- [Public](#public-cluster-setup): Upload Docker image to Dockerhub (or any public Docker registry).
- [Private](#private-cluster-setup): Upload Docker image to private registry. Authentication needs then to be handled for Kubernetes. 

```note
Currently it looks like the `autoscaler.yaml` file might only be used for public.yaml
For private deployments, we might have to use KubeRay
1. https://github.com/GoogleCloudPlatform/ai-on-gke/tree/main/ray-on-gke
2. https://www.paulsblog.dev/how-to-install-a-private-docker-container-registry-in-kubernetes/
```

## Prerequisites

Make sure Autotuner prerequisites are installed. To do so, refer to the installation script.

```bash
pip install ray google-api-python-client cryptography
```

## Public cluster setup

0. Authenticate the necessary GCP account with enough privileges to do:
- `setIamPolicy`

```bash
gcloud auth application-default login
```

1. Set up `.env` with Docker registry username/password. Also, set up the `public.yaml`
file accordingly to your desired specifications.

```bash
cp .env.sample .env
cp public.yaml.template public.yaml
```

2. Run the following commands to build, tag and upload the public image:

```bash
make clean
make base
make docker
make upload
```

3. Launch your cluster as follows:

```bash
make up
```

## Private cluster setup

Coming soon.
