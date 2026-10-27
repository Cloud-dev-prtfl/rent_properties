# Terraform: not used (superseded)

The AWS/Terraform design was superseded by portable hosting on PaaS or self-hosted servers
([ADR-0014](../../docs/adr/0014-portable-hosting-paas-and-self-hosted.md)). Deployment manifests live in
the repository root (`render.yaml`, `fly.toml`, `heroku.yml`, `Procfile`) and in [`deploy/`](../../deploy/README.md).

Terraform (or Ansible) may still be added later to provision VPS hosts, DNS and Cloudflare. Its scope will be
decided with the hosting target (OQ-50).
