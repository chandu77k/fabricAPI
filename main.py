from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.get("/")
def root():
    return {"message": "QuickBooks FastAPI App is running"}


@app.get("/quickbooks/connect")
def quickbooks_connect():
    client_id = os.getenv("CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")
    scope = os.getenv("SCOPE")
    state = "secure_random_state"  # Replace with a dynamic state in production

    base_url = "https://appcenter.intuit.com/connect/oauth2"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state
    }

    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=auth_url)


@app.api_route("/quickbooks/disconnect", methods=["GET", "POST"])
async def quickbooks_disconnect(request: Request):
    try:
        if request.method == "POST":
            payload = await request.json()
        else:
            payload = dict(request.query_params)

        print("Received disconnect payload:", payload)
        return JSONResponse(status_code=200, content={"status": "disconnected"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/eula")
def get_eula():
    return FileResponse("eula.html", media_type="text/html")


@app.get("/privacy-policy")
def get_privacy_policy():
    return FileResponse("privacy-policy.html", media_type="text/html")

@app.get("/quickbooks/callback")
async def quickbooks_callback(request: Request):
    params = dict(request.query_params)
    code = params.get("code")
    state = params.get("state")
    realm_id = params.get("realmId")  # Company ID

    if not code:
        return JSONResponse(status_code=400, content={"error": "Missing authorization code"})

    return {
        "auth_code": code,
        "state": state,
        "realmId": realm_id
    }
