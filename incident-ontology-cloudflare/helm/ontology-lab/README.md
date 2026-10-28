# Ontology Lab Helm chart

Deploys the static learning site only. It replays recorded engine output and does not run Open Ontologies, an AI model, a database, or a live API. The existing Cloudflare Worker is a separate deployment and remains unchanged.

Prerequisites: Docker (or compatible image builder), a container registry reachable by the cluster, Helm 3, and Kubernetes. For public access, install an ingress controller, configure DNS, and provide a TLS secret separately.

From the `incident-ontology-cloudflare` directory, substitute your registry path:

```sh
docker build -t registry.example.com/ontology-lab:1.0.0 .
docker push registry.example.com/ontology-lab:1.0.0
helm upgrade --install ontology-lab ./helm/ontology-lab --namespace ontology-lab --create-namespace --set image.repository=registry.example.com/ontology-lab --set image.tag=1.0.0
kubectl -n ontology-lab port-forward service/ontology-lab-ontology-lab 8080:80
```

Visit http://localhost:8080. To use ingress, add `--set ingress.enabled=true --set ingress.className=YOUR_CLASS --set ingress.host=YOUR_HOST --set ingress.tlsSecretName=YOUR_EXISTING_SECRET`. Ensure DNS points to your ingress controller. Without a TLS secret, the chart configures HTTP only. Consult `values.yaml` for resources, replicas and annotations. No credentials or cluster-wide roles are required by the chart.

Before deploying, render with `helm lint ./helm/ontology-lab --set image.repository=registry.example.com/ontology-lab` and `helm template ontology-lab ./helm/ontology-lab --set image.repository=registry.example.com/ontology-lab`. For a private registry, configure image pull access through your namespace's service account or Kubernetes cluster policy.
