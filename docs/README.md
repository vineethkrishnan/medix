# Medix Docs

This folder holds the [Astro Starlight](https://starlight.astro.build/)
documentation site for Medix. It is deployed to Cloudflare Pages on every
push to `main` that touches `docs/`.

## Local development

```bash
cd docs
npm install
npm run dev
```

Open http://localhost:4321.

## Build

```bash
npm run build
```

The static site is emitted to `docs/dist/`.

## Search

Search is provided by [Pagefind](https://pagefind.app/), built into
Starlight. It's free, client-side, zero-config, and runs as part of
`npm run build` — no external service, no API keys.

## Deployment

See `.github/workflows/deploy-docs.yml`. Deployment uses
`cloudflare/wrangler-action@v3` and expects two repository secrets:

- `CLOUDFLARE_API_TOKEN` — a Cloudflare API token with the
  `Cloudflare Pages: Edit` permission
- `CLOUDFLARE_ACCOUNT_ID` — your Cloudflare account ID

And a Cloudflare Pages project named `medix`. See the main README for
setup instructions.
