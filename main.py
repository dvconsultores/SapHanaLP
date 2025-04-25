from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sap_integration import call_sap_service

app = FastAPI()

# Define the request model
class SAPRequest(BaseModel):
    IBudat: str
    ICharg: str
    IErfmg: float
    ILgort: str
    IMatnr: str
    IMblnr: str
    IProceso: str
    IWerks: str

@app.post("/sap/call")
async def call_sap(request: SAPRequest):
    """Endpoint to call the SAP SOAP service."""
    params = request.model_dump()  # Use model_dump instead of dict
    result = call_sap_service(params)

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result