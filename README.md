# Kubernetes Go and Redis service

# Overview

This repository houses a robust Golang service that operates a single endpoint: `/:id`. Each invocation of this endpoint increments a counter and returns the count of times the endpoint has been accessed for the specified ID. The application's state is managed via Redis, where the data is stored with `id` as the key and the count as the value.

The application, along with its dependencies (Redis in this case), is designed to be deployed on Kubernetes. It is externally accessible via HTTP and is architected with high-availability in mind, ensuring resilience and uptime even in the event of instance failures. The application and Redis are deployed as separate services, each with their own deployments and horizontal pod autoscalers to ensure scalability and high availability.

The Redis service is secured using a Kubernetes Secret to store the password, and its data is stored in a Persistent Volume Claim to ensure data persistence across pod restarts. The Golang application is exposed externally via a LoadBalancer service, and it communicates with the Redis service within the cluster.

The entire solution is engineered to operate seamlessly on a fresh Ubuntu VM, providing a streamlined deployment process. It includes a Python script for stress testing the deployment, ensuring that the application can handle high loads and scale appropriately.

The repository also provides detailed instructions on how to connect to the pod, build the Docker image, perform rolling updates, set up liveness and readiness probes, configure resource requests and limits, and secu

# Table of Contents
- [Kubernetes Go and Redis service](#kubernetes-go-and-redis-service)
- [Overview](#overview)
- [Table of Contents](#table-of-contents)
- [Requirements](#requirements)
- [Components](#components)
  - [Go-lang App](#go-lang-app)
  - [Redis](#redis)
- [Stress testing the deployment](#stress-testing-the-deployment)
- [Useful Info](#useful-info)
  - [Connecting to the pod](#connecting-to-the-pod)
  - [Building the Docker image](#building-the-docker-image)
  - [Update Strategy: Rolling Update](#update-strategy-rolling-update)
  - [Liveness and Readiness Probes](#liveness-and-readiness-probes)
  - [Resource Requests and Limits](#resource-requests-and-limits)
  - [Securing the Redis Pod](#securing-the-redis-pod)
  - [Horizontal Pod Autoscaler](#horizontal-pod-autoscaler)
    - [Skip the certificate verification in metrics server:](#skip-the-certificate-verification-in-metrics-server)



# Requirements

- Simple to build and run
- Application is able to be deployed on kubernetes and can be accessed from outside the cluster
- Application must be able to survive the failure of one or more instances while staying highly-available
- Redis must be password protected 

# Components
## Go-lang App
The Go-lang app manifests consist of the following resources:

- Deployment: Deploys the Go-lang app containers with specified resources, liveness and readiness probes, and environment variables.
- HorizontalPodAutoscaler: Automatically scales the Go-lang app based on CPU utilization.
- Service: Exposes the Go-lang app as a LoadBalancer service on port 80.

## Redis
The Redis manifests consist of the following resources:

- Deployment: Deploys the Redis container with specified resources, liveness and readiness probes, environment variables, and volume mounts.
- HorizontalPodAutoscaler: Automatically scales Redis based on CPU utilization.
- PersistentVolumeClaim: Requests storage for Redis data.
- Secret: Stores the Redis password securely.
- Service: Exposes Redis as a service on port 6379.


# Stress testing the deployment
This repository contains a Python script(`script/locust.py`) using the Locust framework to perform load testing on a deployment. The script simulates concurrent user traffic and measures the performance of the deployment under load.
To test, I advice going to the `load_test` branch in the repository. The average CPU utilization for the app are set to 4% which is ideal for the service.

Set the following variables according to your desired configuration:
- number_of_users: Total number of concurrent users that will be simulated in the load test.
- spawn_rate: Rate at which users are spawned per second.
- duration_in_seconds: Total duration for which the load test will run.

# Useful Info
## Connecting to the pod
```
kubectl exec -it <pod> -- /bin/sh
```

## Building the Docker image
Read this [doc](https://docs.docker.com/registry/deploying/) to push the image to your local docker registry

**commands**:
```
docker run -d -p 5000:5000 --restart=always --name registry registry:2
docker build . -t simple-go-service
docker tag simple-go-service localhost:5000/simple-go-service
docker push localhost:5000/simple-go-service

# Removing locally-cached image
docker image remove simple-go-service
docker image remove localhost:5000/simple-go-service

# You can still pull from your local registry
docker pull localhost:5000/my-ubuntu
```

## Update Strategy: Rolling Update
Rolling updates gradually update Pods instances with new ones. This is done in a controlled way that ensures that at least one instance of your application is available during the update.

Two important parameters in this strategy are:

- maxUnavailable: This is the maximum number of Pods that can be unavailable during the update process. The value can be an absolute number (for example, 1) or a percentage of desired Pods (for example, 10%). The absolute number is calculated from the percentage by rounding down.

- maxSurge: This is the maximum number of Pods that can be scheduled above the original number of Pods. The value can also be an absolute number or a percentage of desired Pods. The absolute number is calculated from percentage by rounding up.

To start a rolling update (e.g for cases where there is a new latest image):
```
kubectl set env deployment/go-lang-app UPDATE_TIMESTAMP="$(date)" # Trigger a rolling update an environment variable
kubectl rollout status deployment/go-lang-app # check status
```

## Liveness and Readiness Probes
- livenessProbe: Kubernetes uses liveness probes to know when to restart a Container. If the liveness probe fails, the Container is restarted.

- readinessProbe: Readiness probes are used to decide when the Container is ready to start accepting traffic. If the readiness probe fails, the Pod is marked as Unready. 

params:
- `initialDelaySeconds`: ives your container some time to initialize and start up before Kubernetes starts checking its health or readiness.
- `periodSeconds`: determines how often Kubernetes will check the health or readiness of your container after the initial delay

## Resource Requests and Limits

- Requests: The resources a Pod is guaranteed to have. Used by Kubernetes to decide where to place Pods.

- Limits: The maximum resources a Pod can use. If a Pod exceeds its limit, Kubernetes will intervene (e.g., by throttling CPU or terminating the Pod).

Remember, if set, `requests` should be less than or equal to `limits`. If they're not set, Kubernetes uses default values based on node capacity.

## Securing the Redis Pod

The Redis database is protected using the following measures:

- **Secret:** A secret named `redis-secret` is created to store the Redis password. The password is stored in base64-encoded format.

- **Persistent Volume Claim:** A persistent volume claim named `redis-pvc` is created to provide persistent storage for the Redis data. It has a storage request of 1Gi.

- **ConfigMap:** A ConfigMap named `redis-config` is created to store the Redis configuration. The Redis password is injected into the `redis.conf` file using the `${REDIS_PASSWORD}` placeholder.

- **Deployment:** A deployment named `redis` is created to manage the Redis container. The Redis image used is `redis:6.2-alpine`. The Redis password is provided as an environment variable (`REDIS_PASSWORD`) sourced from the `redis-secret` secret. The deployment ensures that only one replica of the Redis pod is available at any given time during rolling updates. Resource limits and requests are defined for the container.

- **Volumes:** Two volumes are used by the Redis container. The first one is a persistent volume claim (`redis-pvc`) used for storing the Redis data. The second volume is a config map (`redis-config`) used to provide the Redis configuration.

- **Probes:** Readiness and liveness probes are configured for the Redis container to ensure its availability. The probes execute Redis commands using the provided password to check the health of the Redis instance.

- **Horizontal Pod Autoscaler:** An autoscaler named `redis-hpa` is created to automatically scale the Redis deployment based on CPU utilization. It ensures a minimum of 1 replica and a maximum of 5 replicas, with a target average CPU utilization of 75%.

- **Service:** A service named `redis` is created to expose the Redis deployment internally. It listens on port 6379.


The configMap block in the provided Kubernetes manifest is used to inject the Redis configuration file into the Redis pod. The data block specifies the key-value pairs for the configuration. In this case, the key is redis.conf, and the value is the content of the Redis configuration file.

When the Redis pod is created, the redis.conf file is mounted as a volume using the configMap volume type. This volume is then mounted at a specific path inside the pod, which is determined by the mountPath specified in the container configuration.

In the given manifest, the redis.conf file from the redis-config ConfigMap is mounted at the root directory (/) of the Redis pod. This means that the Redis configuration file will be available at the path /redis.conf inside the pod.

## Horizontal Pod Autoscaler
The HorizontalPodAutoscaler (HPA) is set to automatically scale the number of Go application pods based on the CPU utilization. The minReplicas is set to 1, meaning there will be at least 1 pod running at all times. The maxReplicas is set to 5, which is the maximum number of pods that can be running at once. The target CPU utilization is set to 50%, meaning if the CPU usage exceeds this threshold, the HPA will add more pods (up to maxReplicas).

The metrics server are required for horizontal pod autoscaler. This will apply the manifest file for the latest release (v0.6.3 at the time of writing) from the metrics server's GitHub repository:
```
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.6.3/components.yaml 
```

### Skip the certificate verification in metrics server:
1. Commmand `kubectl -n kube-system edit deploy metrics-server`
2. Under the spec.template.spec.containers.args section, add the --kubelet-insecure-tls argument like so:
```
- args:
  - --cert-dir=/tmp
  - --secure-port=4443
  - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
  - --kubelet-use-node-status-port
  - --kubelet-insecure-tls
```
3. Save and exit

**IMPORTANT**: While this solution is fine for development environments like Docker Desktop, it is not recommended for production environments because it lowers the security of your cluster. In a production environment, you should use valid certificates with the appropriate Subject Alternative Names (SANs).