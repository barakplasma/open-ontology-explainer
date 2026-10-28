# Open Ontology Explainer

A manager-friendly guide and interactive participant-diagram lab. Live: https://incident-ontology.barakplasma.workers.dev/

The site replays recorded results; it is not connected to a live engine. `incident-ontology-cloudflare/dist` is the editable site. `security-incident-ontology` contains the example, queries and outputs. The static-site Helm chart and **untested draft** engine chart are under `incident-ontology-cloudflare/helm`; read their READMEs before use.

## Cloudflare deployment

The GitHub Actions workflow builds the Worker on changes to `main` and deploys it to the existing `incident-ontology` Worker. Before it can run, create repository Actions secrets `CLOUDFLARE_API_TOKEN` (a scoped token with Workers Scripts Edit access for the correct account) and `CLOUDFLARE_ACCOUNT_ID`. Never commit credentials. The workflow also supports manual dispatch. Until those secrets are configured and a run succeeds, the repository is not actually connected to the live site.

To build locally from this repository root: `python3 incident-ontology-cloudflare/build.py`. To update engine output, follow `security-incident-ontology/README.md`, regenerate the downloadable example ZIP at the repo root, and run the build. The deployment uses the generated `worker.mjs`; do not edit it by hand.

The engine Kubernetes chart does not provision a cluster. It requires a cluster, a pre-created token Secret, storage and validation; see its README. The public Cloudflare demo and the Kubernetes engine are separate deployments.
