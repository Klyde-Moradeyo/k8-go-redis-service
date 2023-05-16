# k8-go-redis-service

## Overview

This repository contains a simple golang service which serves a single endpoint: `/:id`. For each call to this endpoint, the service increments a counter, and returns the number of times the endpoint has been called for the given ID. State for the application is stored in and retrieved from redis, where the data is stored simply with `id` as the key, and the count as the value.

I am going to deploy this application, and all its dependencies (in this case, redis) on kubernetes. It will be accessible from outside the cluster via HTTP, and should be deployed with high-availability in mind

The entire solution should be able to run on an fresh ubuntu VM.

## Requirements

- Simple to build and run
- Application is able to be deployed on kubernetes and can be accessed from outside the cluster
- Application must be able to survive the failure of one or more instances while staying highly-available
- Redis must be password protected


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

# Resource Requests and Limits

- Requests: The resources a Pod is guaranteed to have. Used by Kubernetes to decide where to place Pods.

- Limits: The maximum resources a Pod can use. If a Pod exceeds its limit, Kubernetes will intervene (e.g., by throttling CPU or terminating the Pod).

Remember, if set, `requests` should be less than or equal to `limits`. If they're not set, Kubernetes uses default values based on node capacity.