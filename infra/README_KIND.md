# Prometheus & Grafana (lightweight) for KIND

You can deploy a lightweight Prometheus + Grafana stack using kube-prometheus-stack or prometheus-operator, but that may be heavy.
For practice, use the Prometheus community kube-prometheus-stack helm chart or the simple prometheus + grafana manifests.

Example using Helm (requires helm installed):
1. Add repo:
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update

2. Install:
   kubectl create ns monitoring
   helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

3. Configure scrape for the fraud-model service (scrape via ClusterIP service name: fraud-model-svc.mlops.svc.cluster.local:80/metrics)

4. Port-forward grafana:
   kubectl -n monitoring port-forward svc/prometheus-grafana 3000:80

Login with default creds (admin/prom-operator) or check helm notes.

