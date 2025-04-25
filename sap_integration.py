from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3
from dotenv import load_dotenv
import os
from xml.etree import ElementTree as ET

# Load environment variables
load_dotenv()

# Suppress warnings about unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Set endpoint and authentication
endpoint = "https://vhemsds4ci.sap.liderpollo.com:44300/vhemsws1wd01"
username = os.getenv('SAP_USER')
password = os.getenv('SAP_PASSWORD')

# Session setup
session = Session()
session.auth = HTTPBasicAuth(username, password)
session.verify = False  # WARNING: Only use in test/dev environments!
session.headers.update({
    'Content-Type': 'text/xml;charset=UTF-8',
    'SOAPAction': 'urn:sap-com:document:sap:soap:functions:mc-style:ZwsTasaMortalidad'
})

def create_soap_envelope(params):
    """Create SOAP envelope with parameters"""
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:urn="urn:sap-com:document:sap:soap:functions:mc-style">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:ZwsTasaMortalidad>
         <IBudat>{params['IBudat']}</IBudat>
         <ICharg>{params['ICharg']}</ICharg>
         <IErfmg>{params['IErfmg']}</IErfmg>
         <ILgort>{params['ILgort']}</ILgort>
         <IMatnr>{params['IMatnr']}</IMatnr>
         <IMblnr>{params['IMblnr']}</IMblnr>
         <IProceso>{params['IProceso']}</IProceso>
         <IWerks>{params['IWerks']}</IWerks>
      </urn:ZwsTasaMortalidad>
   </soapenv:Body>
</soapenv:Envelope>"""
    return envelope

def call_sap_service(params):
    """Call the SAP SOAP service with the given parameters."""
    try:
        # Create and send SOAP request
        print(f"Attempting SOAP call to: {endpoint}")
        soap_envelope = create_soap_envelope(params)
        response = session.post(endpoint, data=soap_envelope)
        response.raise_for_status()

        # Parse and return response
        root = ET.fromstring(response.content)
        response_data = {}
        for elem in root.iter():
            if elem.text and elem.text.strip():
                response_data[elem.tag] = elem.text
        return {"status": "success", "data": response_data}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# SAP SOAP parameters
params = {
    "IBudat": "2023-08-08",
    "ICharg": "08082023M2",
    "IErfmg": 105,
    "ILgort": "1006",
    "IMatnr": "125001",
    "IMblnr": "5000112373",
    "IProceso": "C",
    "IWerks": "5000",
}

# # Example usage
# if __name__ == "__main__":
#     # Example usage
#     response = call_sap_service(params)
#     print(response)