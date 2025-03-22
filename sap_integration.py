from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3
import requests

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
# wsdl_url = "https://vhemsds4ci.sap.liderpollo.com:8000/sap/bc/srt/wsdl/flv_10002A111AD1/bndg_url/sap/bc/srt/rfc/sap/zws_services_api/150/zws_services_api/zws_services_api?sap-client=150"
wsdl_url = "https://vhemsws1wd01.sap.liderpollo.com:44380/sap/bc/srt/wsdl/flv_10002A111AD1/bndg_url/sap/bc/srt/rfc/sap/zws_services_api/150/zws_services_api/zws_services_api?sap-client=150"

# Authentication setup
username = "ABAPMAR"
password = "Abap**2024"

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
        "I_CHARG": "12345",  # Lote
        "I_BUDAT": "2024-11-26",  # Fecha de contabilización
        "I_ERFMG": 1000,  # Cantidad
        "I_WERKS": "G123",  # Granjas Id
        "I_LGORT": "Galpón1",  # Galpón
        "I_MBLNR": "ORD456",  # Orden de recepción
        "I_MATNR": "Mat789",  # Material
        "I_PROCESO": "Cria",  # Proceso
    }

    # Call the service method
    response = client.service.ZWS_Services_API(**params)
    print("Response from SAP:", response)
except requests.exceptions.RequestException as e:
    print(f"Redirect or network error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
