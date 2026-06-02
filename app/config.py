import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SenderAddress:
    name: str
    street: str
    house: str
    zip: str
    city: str
    country: str = "DEU"
    email: str = ""
    phone: str = ""


@dataclass
class Config:
    dhl_client_id: str
    dhl_client_secret: str
    dhl_gkp_user: str
    dhl_gkp_password: str
    dhl_ekp: str
    dhl_partner_no: str
    dhl_test_mode: bool
    dhl_profile: str
    label_format: str
    sender: SenderAddress
    printnode_api_key: str
    printnode_printer_id: int
    products_file: str
    log_retention_days: int | None


def load_config() -> Config:
    return Config(
        dhl_client_id=os.environ["DHL_CLIENT_ID"],
        dhl_client_secret=os.environ["DHL_CLIENT_SECRET"],
        dhl_gkp_user=os.environ["DHL_GKP_USER"],
        dhl_gkp_password=os.environ["DHL_GKP_PASSWORD"],
        dhl_ekp=os.environ["DHL_EKP"],
        dhl_partner_no=os.environ.get("DHL_PARTNER_NO", "01"),
        dhl_test_mode=os.environ.get("DHL_TEST_MODE", "false").lower() == "true",
        dhl_profile=os.environ.get("DHL_PROFILE", "STANDARD_GRUPPENPROFIL"),
        label_format=os.environ.get("LABEL_FORMAT", "A4"),
        sender=SenderAddress(
            name=os.environ["SENDER_NAME"],
            street=os.environ["SENDER_STREET"],
            house=os.environ["SENDER_HOUSE"],
            zip=os.environ["SENDER_ZIP"],
            city=os.environ["SENDER_CITY"],
            country=os.environ.get("SENDER_COUNTRY", "DEU"),
            email=os.environ.get("SENDER_EMAIL", ""),
            phone=os.environ.get("SENDER_PHONE", ""),
        ),
        printnode_api_key=os.environ["PRINTNODE_API_KEY"],
        printnode_printer_id=int(os.environ["PRINTNODE_PRINTER_ID"]),
        products_file=os.environ.get("PRODUCTS_FILE", "/app/products.yaml"),
        log_retention_days=int(os.environ["LOG_RETENTION_DAYS"]) if os.environ.get("LOG_RETENTION_DAYS") else None,
    )


def load_products(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def select_product(products: dict, weight_g: int, domestic: bool) -> str:
    """Return best product code for given weight and destination."""
    candidates = {
        code: p for code, p in products.items()
        if p.get("domestic", True) == domestic
    }
    # Prefer weight-limited products (Warenpost) when weight fits
    for code, p in sorted(candidates.items(), key=lambda x: x[1].get("max_weight_g", 999999)):
        max_w = p.get("max_weight_g")
        if max_w is None or weight_g <= max_w:
            return code
    # Fallback: heaviest-capable product
    return max(candidates, key=lambda c: candidates[c].get("max_weight_g", 999999))
