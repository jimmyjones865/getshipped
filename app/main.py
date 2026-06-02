import re
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

from config import load_config, load_products, select_product
from dhl_client import DHLClient, parse_address_text
from printnode import print_label
from db import init_db, log_label, get_labels, purge_old_labels

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

config = load_config()
products = load_products(config.products_file)
dhl = DHLClient(config, products)

app = FastAPI()
init_db()
if config.log_retention_days:
    purge_old_labels(config.log_retention_days)


class ShipRequest(BaseModel):
    name: str
    street: str
    house: str = ""
    zip: str
    city: str
    country: str = "DE"
    email: str = ""
    weight_g: int
    product_code: str = ""
    ref_no: str = ""

    @field_validator("weight_g")
    @classmethod
    def weight_positive(cls, v):
        if v <= 0:
            raise ValueError("weight must be positive")
        return v


class ParseRequest(BaseModel):
    text: str


def _auto_ref() -> str:
    return datetime.now(timezone.utc).strftime("GS-%Y%m%d-%H%M%S")


@app.get("/api/products")
def api_products():
    return [
        {"code": code, "name": p["name"], "max_weight_g": p.get("max_weight_g"), "domestic": p.get("domestic", True)}
        for code, p in products.items()
    ]


@app.post("/api/parse-address")
def api_parse_address(req: ParseRequest):
    return parse_address_text(req.text)


@app.post("/api/ship")
def api_ship(req: ShipRequest):
    domestic = req.country.upper().strip() in ("DE", "DEU")

    product_code = req.product_code
    if not product_code:
        product_code = select_product(products, req.weight_g, domestic)

    product = products.get(product_code)
    if not product:
        raise HTTPException(400, f"Unknown product code: {product_code}")

    max_w = product.get("max_weight_g")
    if max_w and req.weight_g > max_w:
        raise HTTPException(400, f"{product['name']} max weight is {max_w}g")

    ref_no = req.ref_no.strip() or _auto_ref()

    recipient = {
        "name": req.name,
        "street": req.street,
        "house": req.house,
        "zip": req.zip,
        "city": req.city,
        "country": req.country,
        "email": req.email,
    }

    try:
        result = dhl.create_shipment(recipient, req.weight_g, product_code, ref_no)
    except Exception as e:
        log.error("DHL API error: %s", e)
        raise HTTPException(502, f"DHL API error: {e}")

    # Extract first shipment item from response
    items = result.get("items", [])
    if not items:
        detail = result.get("title") or result.get("detail") or str(result)
        raise HTTPException(502, f"DHL error: {detail}")

    item = items[0]
    status = item.get("sstatus", {})
    status_code = status.get("status", 0)

    if status_code >= 400:
        msg = status.get("detail") or status.get("title") or "Unknown DHL error"
        raise HTTPException(502, f"DHL rejected shipment: {msg}")

    tracking = item.get("shipmentNo", "")
    label_b64 = item.get("label", {}).get("b64", "")

    warnings = []
    if status_code not in (200, 201) and status.get("detail"):
        warnings.append(status["detail"])

    # Print label
    printed = False
    if label_b64:
        try:
            print_label(config.printnode_api_key, config.printnode_printer_id, label_b64,
                        title=f"DHL {tracking}")
            printed = True
        except Exception as e:
            log.error("PrintNode error: %s", e)
            warnings.append(f"Druckfehler: {e}")

    # Log to DB
    try:
        log_label(
            recipient_name=req.name,
            recipient_zip=req.zip,
            recipient_city=req.city,
            recipient_country=req.country.upper(),
            product_code=product_code,
            product_name=product["name"],
            weight_g=req.weight_g,
            tracking_number=tracking,
            ref_no=ref_no,
        )
    except Exception as e:
        log.error("DB log error: %s", e)

    return {
        "tracking_number": tracking,
        "product": product["name"],
        "printed": printed,
        "warnings": warnings,
        "ref_no": ref_no,
    }


@app.get("/api/labels")
def api_labels():
    return get_labels(50)


@app.get("/")
def index():
    return FileResponse("/app/static/index.html")


app.mount("/static", StaticFiles(directory="/app/static"), name="static")
