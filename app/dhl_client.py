import re
import time
import requests
from datetime import date

_COUNTRY_MAP = {
    'AW': 'ABW', 'AF': 'AFG', 'AO': 'AGO', 'AI': 'AIA', 'AX': 'ALA',
    'AL': 'ALB', 'AD': 'AND', 'AE': 'ARE', 'AR': 'ARG', 'AM': 'ARM',
    'AS': 'ASM', 'AG': 'ATG', 'AU': 'AUS', 'AT': 'AUT', 'AZ': 'AZE',
    'BI': 'BDI', 'BE': 'BEL', 'BJ': 'BEN', 'BQ': 'BES', 'BF': 'BFA',
    'BD': 'BGD', 'BG': 'BGR', 'BH': 'BHR', 'BS': 'BHS', 'BA': 'BIH',
    'BL': 'BLM', 'BY': 'BLR', 'BZ': 'BLZ', 'BM': 'BMU', 'BO': 'BOL',
    'BR': 'BRA', 'BB': 'BRB', 'BN': 'BRN', 'BT': 'BTN', 'BV': 'BVT',
    'BW': 'BWA', 'CF': 'CAF', 'CA': 'CAN', 'CC': 'CCK', 'CH': 'CHE',
    'CL': 'CHL', 'CN': 'CHN', 'CI': 'CIV', 'CM': 'CMR', 'CD': 'COD',
    'CG': 'COG', 'CK': 'COK', 'CO': 'COL', 'KM': 'COM', 'CV': 'CPV',
    'CR': 'CRI', 'CU': 'CUB', 'CW': 'CUW', 'CX': 'CXR', 'KY': 'CYM',
    'CY': 'CYP', 'CZ': 'CZE', 'DE': 'DEU', 'DJ': 'DJI', 'DM': 'DMA',
    'DK': 'DNK', 'DO': 'DOM', 'DZ': 'DZA', 'EC': 'ECU', 'EG': 'EGY',
    'ER': 'ERI', 'ES': 'ESP', 'EE': 'EST', 'ET': 'ETH', 'FI': 'FIN',
    'FJ': 'FJI', 'FK': 'FLK', 'FR': 'FRA', 'FO': 'FRO', 'FM': 'FSM',
    'GA': 'GAB', 'GB': 'GBR', 'GE': 'GEO', 'GG': 'GGY', 'GH': 'GHA',
    'GI': 'GIB', 'GN': 'GIN', 'GP': 'GLP', 'GM': 'GMB', 'GW': 'GNB',
    'GQ': 'GNQ', 'GR': 'GRC', 'GD': 'GRD', 'GL': 'GRL', 'GT': 'GTM',
    'GF': 'GUF', 'GU': 'GUM', 'GY': 'GUY', 'HK': 'HKG', 'HM': 'HMD',
    'HN': 'HND', 'HR': 'HRV', 'HT': 'HTI', 'HU': 'HUN', 'ID': 'IDN',
    'IM': 'IMN', 'IN': 'IND', 'IE': 'IRL', 'IR': 'IRN', 'IQ': 'IRQ',
    'IS': 'ISL', 'IL': 'ISR', 'IT': 'ITA', 'JM': 'JAM', 'JE': 'JEY',
    'JO': 'JOR', 'JP': 'JPN', 'KZ': 'KAZ', 'KE': 'KEN', 'KG': 'KGZ',
    'KH': 'KHM', 'KI': 'KIR', 'KN': 'KNA', 'KR': 'KOR', 'KW': 'KWT',
    'LA': 'LAO', 'LB': 'LBN', 'LR': 'LBR', 'LY': 'LBY', 'LC': 'LCA',
    'LI': 'LIE', 'LK': 'LKA', 'LS': 'LSO', 'LT': 'LTU', 'LU': 'LUX',
    'LV': 'LVA', 'MO': 'MAC', 'MF': 'MAF', 'MA': 'MAR', 'MC': 'MCO',
    'MD': 'MDA', 'MG': 'MDG', 'MV': 'MDV', 'MX': 'MEX', 'MH': 'MHL',
    'MK': 'MKD', 'ML': 'MLI', 'MT': 'MLT', 'MM': 'MMR', 'ME': 'MNE',
    'MN': 'MNG', 'MP': 'MNP', 'MZ': 'MOZ', 'MR': 'MRT', 'MS': 'MSR',
    'MQ': 'MTQ', 'MU': 'MUS', 'MW': 'MWI', 'MY': 'MYS', 'YT': 'MYT',
    'NA': 'NAM', 'NC': 'NCL', 'NE': 'NER', 'NF': 'NFK', 'NG': 'NGA',
    'NI': 'NIC', 'NU': 'NIU', 'NL': 'NLD', 'NO': 'NOR', 'NP': 'NPL',
    'NR': 'NRU', 'NZ': 'NZL', 'OM': 'OMN', 'PK': 'PAK', 'PA': 'PAN',
    'PN': 'PCN', 'PE': 'PER', 'PH': 'PHL', 'PW': 'PLW', 'PG': 'PNG',
    'PL': 'POL', 'PR': 'PRI', 'KP': 'PRK', 'PT': 'PRT', 'PY': 'PRY',
    'PS': 'PSE', 'PF': 'PYF', 'QA': 'QAT', 'RE': 'REU', 'RO': 'ROU',
    'RU': 'RUS', 'RW': 'RWA', 'SA': 'SAU', 'SD': 'SDN', 'SN': 'SEN',
    'SG': 'SGP', 'SH': 'SHN', 'SJ': 'SJM', 'SB': 'SLB', 'SL': 'SLE',
    'SV': 'SLV', 'SM': 'SMR', 'SO': 'SOM', 'PM': 'SPM', 'RS': 'SRB',
    'SS': 'SSD', 'ST': 'STP', 'SR': 'SUR', 'SK': 'SVK', 'SI': 'SVN',
    'SE': 'SWE', 'SZ': 'SWZ', 'SX': 'SXM', 'SC': 'SYC', 'SY': 'SYR',
    'TC': 'TCA', 'TD': 'TCD', 'TG': 'TGO', 'TH': 'THA', 'TJ': 'TJK',
    'TK': 'TKL', 'TM': 'TKM', 'TL': 'TLS', 'TO': 'TON', 'TT': 'TTO',
    'TN': 'TUN', 'TR': 'TUR', 'TV': 'TUV', 'TW': 'TWN', 'TZ': 'TZA',
    'UG': 'UGA', 'UA': 'UKR', 'UY': 'URY', 'US': 'USA', 'UZ': 'UZB',
    'VA': 'VAT', 'VC': 'VCT', 'VE': 'VEN', 'VG': 'VGB', 'VI': 'VIR',
    'VN': 'VNM', 'VU': 'VUT', 'WF': 'WLF', 'WS': 'WSM', 'YE': 'YEM',
    'ZA': 'ZAF', 'ZM': 'ZMB', 'ZW': 'ZWE',
}


_COUNTRY_NAMES = {
    'GERMANY': 'DEU', 'DEUTSCHLAND': 'DEU',
    'AUSTRIA': 'AUT', 'ÖSTERREICH': 'AUT', 'OESTERREICH': 'AUT',
    'SWITZERLAND': 'CHE', 'SCHWEIZ': 'CHE', 'SUISSE': 'CHE', 'SVIZZERA': 'CHE',
    'FRANCE': 'FRA', 'FRANKREICH': 'FRA',
    'NETHERLANDS': 'NLD', 'NIEDERLANDE': 'NLD', 'HOLLAND': 'NLD',
    'BELGIUM': 'BEL', 'BELGIEN': 'BEL', 'BELGIQUE': 'BEL',
    'ITALY': 'ITA', 'ITALIEN': 'ITA', 'ITALIA': 'ITA',
    'SPAIN': 'ESP', 'SPANIEN': 'ESP', 'ESPAÑA': 'ESP',
    'POLAND': 'POL', 'POLEN': 'POL',
    'CZECH REPUBLIC': 'CZE', 'CZECHIA': 'CZE', 'TSCHECHIEN': 'CZE',
    'DENMARK': 'DNK', 'DÄNEMARK': 'DNK', 'DAENEMARK': 'DNK',
    'SWEDEN': 'SWE', 'SCHWEDEN': 'SWE',
    'NORWAY': 'NOR', 'NORWEGEN': 'NOR',
    'FINLAND': 'FIN', 'FINNLAND': 'FIN',
    'LUXEMBOURG': 'LUX', 'LUXEMBURG': 'LUX',
    'PORTUGAL': 'PRT',
    'HUNGARY': 'HUN', 'UNGARN': 'HUN',
    'ROMANIA': 'ROU', 'RUMÄNIEN': 'ROU', 'RUMAENIEN': 'ROU',
    'SLOVAKIA': 'SVK', 'SLOWAKEI': 'SVK',
    'SLOVENIA': 'SVN', 'SLOWENIEN': 'SVN',
    'CROATIA': 'HRV', 'KROATIEN': 'HRV',
    'BULGARIA': 'BGR', 'BULGARIEN': 'BGR',
    'GREECE': 'GRC', 'GRIECHENLAND': 'GRC',
    'UNITED KINGDOM': 'GBR', 'UK': 'GBR', 'GREAT BRITAIN': 'GBR', 'GROSSBRITANNIEN': 'GBR',
    'ENGLAND': 'GBR', 'SCOTLAND': 'GBR', 'SCHOTTLAND': 'GBR', 'WALES': 'GBR',
    'IRELAND': 'IRL', 'IRLAND': 'IRL',
    'USA': 'USA', 'UNITED STATES': 'USA', 'UNITED STATES OF AMERICA': 'USA',
    'CANADA': 'CAN', 'KANADA': 'CAN',
    'AUSTRALIA': 'AUS', 'AUSTRALIEN': 'AUS',
    'JAPAN': 'JPN',
    'CHINA': 'CHN',
}


def _recognize_country(s: str) -> str | None:
    """Returns alpha-3 code if `s` is a recognized country name or 2/3-letter code, else None."""
    key = s.strip().upper()
    if key in _COUNTRY_NAMES:
        return _COUNTRY_NAMES[key]
    if len(key) == 2 and key in _COUNTRY_MAP:
        return _COUNTRY_MAP[key]
    if len(key) == 3 and key in _COUNTRY_MAP.values():
        return key
    return None


def parse_address_text(text: str) -> dict:
    """Parse pasted address block into structured fields. Best-effort, bottom-up."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    result = {"name": "", "name2": "", "name3": "", "street": "", "house": "", "zip": "", "city": "", "country": "DEU"}
    if not lines:
        return result

    # Country: last line, only if ≥4 lines remain after (need name+street+zip+city)
    if len(lines) >= 4:
        recognized = _recognize_country(lines[-1])
        if recognized:
            result["country"] = recognized
            lines = lines[:-1]

    # Zip + city: last line matching [4-6 alphanumeric] space [rest]
    if lines:
        m = re.match(r'^([A-Z0-9]{4,6})\s+(.+)$', lines[-1], re.IGNORECASE)
        if m:
            result["zip"] = m.group(1).upper()
            result["city"] = m.group(2).strip()
            lines = lines[:-1]

    # Street + house: last line; house is a digit-led token at the end
    if lines:
        m = re.match(r'^(.+?)\s+(\d+[\w/-]*)$', lines[-1])
        if m:
            result["street"] = m.group(1).strip()
            result["house"] = m.group(2).strip()
        else:
            result["street"] = lines[-1]
        lines = lines[:-1]

    # Remaining lines → name1, name2, name3
    if lines:
        result["name"] = lines[0]
    if len(lines) > 1:
        result["name2"] = lines[1]
    if len(lines) > 2:
        result["name3"] = lines[2]

    return result


class DHLClient:
    _TOKEN_URL = {
        True: "https://api-sandbox.dhl.com/parcel/de/account/auth/ropc/v1/token",
        False: "https://api-eu.dhl.com/parcel/de/account/auth/ropc/v1/token",
    }
    _API_URL = {
        True: "https://api-sandbox.dhl.com/parcel/de/shipping/v2",
        False: "https://api-eu.dhl.com/parcel/de/shipping/v2",
    }

    def __init__(self, config, products: dict):
        self.config = config
        self.products = products
        self.token = None
        self._token_expires_at = 0
        self._token_url = self._TOKEN_URL[config.dhl_test_mode]
        self._api_url = self._API_URL[config.dhl_test_mode]

    def login(self):
        resp = requests.post(
            self._token_url,
            data={
                "grant_type": "password",
                "client_id": self.config.dhl_client_id,
                "client_secret": self.config.dhl_client_secret,
                "username": self.config.dhl_gkp_user,
                "password": self.config.dhl_gkp_password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 3600) - 60

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        }

    def _billing_number(self, product_code: str) -> str:
        procedure = self.products.get(product_code, {}).get("procedure", "01")
        return f"{self.config.dhl_ekp}{procedure}{self.config.dhl_partner_no}"

    def _build_address(self, addr: dict, is_sender: bool = False) -> dict:
        result = {
            "name1": addr["name"],
            "addressStreet": addr["street"],
            "postalCode": addr["zip"],
            "city": addr["city"],
            "country": addr.get("country", "DEU").strip().upper(),
        }
        if addr.get("name2"):
            result["name2"] = addr["name2"]
        if addr.get("name3"):
            result["name3"] = addr["name3"]
        if addr.get("house"):
            result["addressHouse"] = addr["house"]
        if addr.get("email"):
            result["email"] = addr["email"]
        if not is_sender and addr.get("phone"):
            result["phone"] = addr["phone"]
        return result

    def create_shipment(self, recipient: dict, weight_g: int, product_code: str, ref_no: str) -> dict:
        """Returns the full API response dict. Caller checks for errors."""
        if not self.token or time.time() >= self._token_expires_at:
            self.login()

        sender = self.config.sender
        shipper_addr = {
            "name": sender.name,
            "street": sender.street,
            "house": sender.house,
            "zip": sender.zip,
            "city": sender.city,
            "country": sender.country,
            "email": sender.email,
            "phone": sender.phone,
        }

        shipment = {
            "product": product_code,
            "billingNumber": self._billing_number(product_code),
            "refNo": ref_no[:35],
            "shipDate": date.today().isoformat(),
            "shipper": self._build_address(shipper_addr, is_sender=True),
            "consignee": self._build_address(recipient),
            "details": {
                "weight": {"uom": "kg", "value": round(weight_g / 1000, 3)},
            },
        }

        body = {
            "profile": self.config.dhl_profile,
            "shipments": [shipment],
        }

        params = {
            "includeDocs": "include",
            "docFormat": "PDF",
            "printFormat": self.config.label_format,
        }

        resp = requests.post(
            self._api_url + "/orders",
            json=body,
            headers=self._headers(),
            params=params,
            timeout=30,
        )
        return resp.json()
