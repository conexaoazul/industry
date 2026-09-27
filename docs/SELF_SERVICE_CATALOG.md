# Industry Self-Service Catalog

This repository is the source of truth for Odoo Industry templates used by the
Conexao Azul self-service journey.

Generate the public catalog with:

```bash
python3 tools/industry_catalog.py
```

The output is deterministic at `catalog/industries.json`. By default only
manifests with `application=True` are published as selectable customer
templates. Support/dependency modules remain installable but are not exposed as
standalone verticals.

Each public entry keeps the original Odoo source references (`source_url` and
`source_website`) for provenance while exposing stable Conexao Azul paths:

- `/segmentos/<slug>` — public SEO/detail page.
- `/go/industry/<slug>` — canonical trial/provisioning entrypoint.

Downstream systems should use the Conexao Azul paths and must not rewrite legal,
license, documentation, SLA, or evidence links that intentionally point to
odoo.com.

The provisioning layer must treat `slug` as an allowlisted catalog key. Browser
input must never become an arbitrary module name, shell argument, image, network,
secret, or Docker label.
