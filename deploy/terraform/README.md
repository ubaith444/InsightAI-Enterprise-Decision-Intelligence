# InsightAI Terraform-Ready Structure

This folder is reserved for cloud-specific Terraform modules.

Recommended modules:

- network: VPC/VNet, subnets, security groups
- compute: Kubernetes cluster or container app service
- data: managed PostgreSQL, MongoDB-compatible store, Redis
- observability: Prometheus/Grafana workspace and log sink
- secrets: cloud secret manager entries for database URLs, JWT secret, OpenAI key, OAuth clients
- storage: object storage for dataset imports and exported reports

Keep provider-specific state outside the application repository and inject runtime values through Kubernetes secrets or the selected cloud secret manager.
