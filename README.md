# get shipt

Internal DHL label printing tool for get-steps. Paste or enter a recipient address, set the weight, and print a label directly to a connected printer via PrintNode.

## Features

- Paste an address block and have it auto-parsed into fields
- Auto-selects product (Warenpost / DHL Paket, domestic / international) based on weight and destination country
- Product codes configurable in `products.yaml` — no code change needed if DHL renames them
- Sends label PDF to PrintNode printer automatically
- Logs all printed labels with tracking number, recipient, product, weight

## Setup

```bash
cp .env.example .env
# Fill in all values in .env
docker compose up -d
```

Access at `http://localhost:8765`.

## Configuration

All runtime config lives in `.env`. See `.env.example` for all variables.

**DHL credentials** — two pairs needed:
- Client ID + Secret: from [developer.dhl.com](https://developer.dhl.com) (your API app)
- GKP User + Password: from the DHL Geschäftskundenportal

**EKP:** 10-digit DHL account number.

**Label format:** `LABEL_FORMAT` maps to DHL's `printFormat` — e.g. `A4`, `910-300-700`, `100x70mm`. Match this to your printer.

**PrintNode:** API key from printnode.com + the numeric printer ID.

## Products

`products.yaml` defines the available DHL products. Edit this file if DHL changes product codes — no rebuild needed (it's copied into the image, so a rebuild is required after changes).

```yaml
V01PAK:
  name: DHL Paket
  procedure: "01"      # used in billing number construction
  max_weight_g: 31500
  domestic: true
```

## Data

Label log is stored in `./data/labels.db` (SQLite). The `data/` directory is mounted as a volume and persists across restarts.

## Rebuild after config changes

```bash
docker compose build
docker compose up -d --force-recreate
```
