import requests
from base64 import b64encode


def print_label(api_key: str, printer_id: int, pdf_b64: str, title: str = "DHL Label") -> bool:
    """Submit a base64 PDF to PrintNode. Returns True on success."""
    resp = requests.post(
        "https://api.printnode.com/printjobs",
        auth=(api_key, ""),
        json={
            "printer": printer_id,
            "title": title,
            "contentType": "pdf_base64",
            "content": pdf_b64,
            "source": "getshipped",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return True
