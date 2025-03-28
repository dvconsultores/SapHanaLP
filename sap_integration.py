from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Suppress warnings about unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NoRedirectSession(Session):
    """Custom session class to detect and prevent redirects."""
    def request(self, method, url, **kwargs):
        # Block redirects explicitly
        kwargs['allow_redirects'] = False
        response = super().request(method, url, **kwargs)
        # Check for redirects and halt execution
        if response.is_redirect:
            raise requests.exceptions.RequestException(
                f"Redirect detected to {response.headers.get('Location')}."
            )
        return response


# Define WSDL and connection settings
wsdl_url = os.getenv('WSDL_URL')

# Authentication setup
username = os.getenv('SAP_USER')
password = os.getenv('SAP_PASSWORD')

# Create a custom session with authentication
session = NoRedirectSession()
session.auth = HTTPBasicAuth(username, password)
session.verify = False  # Disable SSL certificate verification

# Transport setup with session
transport = Transport(session=session)

# Debugging redirects
try:
    response = session.get(wsdl_url)
    if response.status_code == 200:
        print("WSDL fetched successfully.")
    else:
        print(f"Failed to fetch WSDL: {response.status_code} {response.reason}")
except Exception as e:
    print(f"Error fetching WSDL: {e}")
    exit()

try:
    # Create SOAP client
    client = Client(wsdl=wsdl_url, transport=transport)

    # Define parameters
    params = {
        "ICharg": "12345",  # Lote (char10)
        "IBudat": "2024-11-26",  # Fecha de contabilización (date10)
        "IErfmg": 1000,  # Cantidad (quantum13.3)
        "IWerks": "G123",  # Granjas Id (char4)
        "ILgort": "GAL1",  # Galpón (char4) - Note: max 4 chars!
        "IMblnr": "ORD456",  # Orden de recepción (char10)
        "IMatnr": "Mat789",  # Material (char40)
        "IProceso": "Cria",  # Proceso (char10)
    }

    # Call the service method
    response = client.service.ZwsTasaMortalidad(**params)
    print("Response from SAP:", response)
except requests.exceptions.RequestException as e:
    print(f"Redirect or network error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
