---
name: domain-dns-ops
description: "Ryan's Cloudflare DNS, Worker domains, redirects, Email Routing, and tunnel-aware troubleshooting for Plaintext Lab and QRble."
---

# Cloudflare DNS and Domains

Ryan uses Cloudflare for DNS and application infrastructure, not domain registration or purchasing.
Do not buy, transfer, renew, or change registrar delegation as part of a DNS task.

## Verified environment

Checked against the authenticated dashboard and public DNS on 2026-09-16.
This is a starting inventory; reread the affected live records and bindings before changing them.

- Account ID: `dc5fd725e5b9bf83fd68107fbd35367c`.
- Workers subdomain: `red-tracker.workers.dev`.
- Seven active zones: `lumenstrength.com.au`, `metisary.com`, `metisary.com.au`, `oryn.media`, `plaintextlab.com`, `qrble.com`, and `tixbookings.com`.
- `lumenstrength.com.au` and `metisary.com.au` delegate to `isaac.ns.cloudflare.com` / `nucum.ns.cloudflare.com`; the other five use `cory.ns.cloudflare.com` / `zainab.ns.cloudflare.com`.
  Nameservers differ by zone; never copy a pair from another domain.
- The dashboard identifies GoDaddy as the registrar for `plaintextlab.com`; other registrars have not been verified.

## Routing and ownership

| Surface | Verified configuration | Preserve |
| --- | --- | --- |
| `plaintextlab.com` and `www.plaintextlab.com` | Apex A/AAAA records for GitHub Pages; `www` CNAME to `plaintext-lab.github.io`; all DNS-only, labelled `plaintext-blog` | Keep their DNS-only mode unless a deliberate hosting/proxy change is requested. |
| `qrble.com`, `app.qrble.com`, `www.qrble.com` | Production custom domains on Worker `tixbookings` | Manage through the Worker's Domains view; do not replace managed records with manual placeholders. |
| `tixbookings.red-tracker.workers.dev` | Enabled production URL for the same QRble Worker | Existing printed QR codes depend on the legacy Worker name and URL; do not rename or disable it during branding/DNS cleanup. |
| `synapse.red-tracker.workers.dev` | Worker `synapse` | Check its own deployment configuration; do not invent a custom domain. |
| `tesla.plaintextlab.com` | Worker `tesla-oauth-callback` | Preserve the callback hostname; DNS cleanup is not permission to change OAuth routing. |
| `metisary.com.au` | Apex HTTPS returned `301` to `https://metisary.com/` | Inspect the configured redirect owner before editing; an HTTP response alone does not identify the rule or service. |
| `tixbookings-live.pages.dev` | Separate Pages project `tixbookings-live`, with no custom domains and no Git connection | Do not confuse it with QRble's production Worker or delete it as part of DNS work. |
| `plaintextlab-access` | Worker exists; Workers overview reports no active routes | Do not infer that Access protection is absent elsewhere or delete the Worker without a separate request. |

`lumenstrength.com.au` and `oryn.media` are active zones, but their application ownership has not been established here.
`tixbookings.com` is a separate zone from the legacy `tixbookings` Worker name; do not assume it serves or redirects to QRble.

## Mail and tunnels

- `plaintextlab.com` has Cloudflare Email Routing MX records, SPF, DKIM, and DMARC.
  Preserve these during website changes; use Email Routing for its managed records.
- `tixbookings.com` has a Microsoft mail-protection MX target.
  Do not replace it with the Plaintext Lab mail configuration.
- `plaintextlab.com` includes a proxied wildcard and an explicit hostname connected to an existing Cloudflare Tunnel.
  Inspect the live tunnel mapping, ingress, and applicable Access policies before changing a matching hostname.
  Adding an explicit record can change which service receives traffic previously covered by the wildcard.
- Keep private tunnel identifiers, origin addresses, access policies, credentials, and raw account exports out of this repository.

## Tools and source of truth

Use the available Cloudflare MCP/API tools for scoped reads and authorised changes; discover their schema first.
The configured MCP is named `cloudflare-api` at `https://mcp.cloudflare.com/mcp`.
Verify authentication and the account ID above before acting; a configured server is not proof of access.
If unavailable, use the authenticated dashboard through the available browser/computer-use tools.
Never extract browser cookies or print credentials to work around failed authentication.

Live Cloudflare state owns dashboard-managed DNS, redirects, and domain bindings.
For deployment changes, locate and verify the owning checkout, then read its `AGENTS.md`, deployment docs, and `wrangler.toml` or `wrangler.jsonc`.
QRble's configuration uses Worker `tixbookings`, R2 `qr-flyer-files`, D1 `tixbookings-scans`, and KV bindings `AUTH`, `QRCODES`, `RATE_LIMIT`, and `TEMPLATES`.
Synapse's configuration uses Worker `synapse`, D1 `adhd-tracker`, static assets, Browser Rendering, and a cron trigger.
Read resource IDs from the owning configuration and confirm live bindings; do not recreate resources to match product names.

## Change and verify

1. Identify the exact zone, hostname, record or rule, and owning service.
   Inspect existing A/AAAA/CNAME records, proxy mode, TTL, mail records, wildcard coverage, and relevant Worker/Pages/tunnel bindings.
2. Record the current affected values privately for rollback, then make only the requested change through its owning service.
   Do not add dummy apex/wildcard records, disable bot protection, or alter Access policies as a default DNS step.
3. Read back the changed configuration and verify the relevant DNS answer with both the zone's authoritative nameserver and a recursive resolver, accounting for TTL.
   For web changes, check HTTPS and the intended host/path; verify status and `Location` for redirects, including path/query handling where required.
4. Report the actual result and any propagation or authentication limitation.
   Check mail DNS when affected; a DNS lookup alone does not prove mail delivery or tunnel health.

Example read-only checks for QRble:

```bash
dig @cory.ns.cloudflare.com qrble.com A +noall +answer
dig @1.1.1.1 qrble.com A +noall +answer
curl --head --max-time 20 https://qrble.com/
```

Successful DNS does not establish that an application works.
Preserve QRble's legacy URL alongside its custom domains when verifying any routing change.
