# ΦField Lab public research dashboard

Live site target: https://michaelwave369.github.io/PhiFieldLab/ (only after the Pages workflow deploys successfully).

## Development

Requires Node 22+.

```sh
cd web
npm install
npm run dev
npm run build
```

Local dev URL uses the repository prefix: http://127.0.0.1:5173/PhiFieldLab/

## What is implemented

- An original responsive React interface, with the E0 sample report/config/manifest imported from the **existing committed scientific artifacts** at build time.
- A separate, synthetic **exact arithmetic** directed-cycle explorer with interactive controls. It never performs neural inference.
- Real sample E0 learned, exact-rule and negative-control scores. The header KPIs always describe the bundled sample.
- Read-only SHA-256 values from the committed manifest, with copy actions (no in-browser verification of the weight bytes).
- Local-only JSON report import for E0-formatted simulated results; allowed shape and size checked; displayed outcomes are always unverified operator claims. No backend, file uploads, telemetry or data storage.
- Explicit research status: **SIMULATED / authority NONE / independent attestation false**.

## Limitations

No independent physics finding, no production inference server, no GPU training on the site, no model weights loaded by JavaScript, and no authority beyond the frozen E0 evidence. There is no claim that the model beats the exact mathematical baseline.

## GitHub Pages

The root `.github/workflows/pages.yml` builds the Vite app on pull requests and deploys its static `web/dist` output only after a change merges to `main`. In repository **Settings → Pages**, choose **GitHub Actions** as the build/deployment source if not already selected. Inspect the deploy job status and the actual Pages URL after merge.

The site's base URL is set to `/PhiFieldLab/`, not `/`. All scientific Python training and model files remain separate and unmodified.
