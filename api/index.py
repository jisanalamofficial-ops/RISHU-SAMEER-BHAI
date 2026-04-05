import requests
import hashlib
from fastapi import FastAPI, Request

# Vercel entrypoint - Sabse upar hona zaroori hai
app = FastAPI()

# --- Garena & Social URLs ---
U_INFO     = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
U_OTP      = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
U_V_OTP    = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
U_BIND     = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
U_V_ID     = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
U_REBIND   = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
U_CANCEL   = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
U_PLAT     = "https://100067.connect.garena.com/bind/app/platform/info/get"
U_RANK     = "https://clientbp.ggwhitehawk.com/GetPlayerCSRankingInfoByAccountID"
U_F_LIST   = "https://clientbp.ggwhitehawk.com/GetFriendRequestList"
U_F_ADD    = "https://clientbp.ggwhitehawk.com/RequestAddingFriend"
U_F_REM    = "https://clientbp.ggwhitehawk.com/RemoveFriend"
U_F_ACC    = "https://clientbp.ggwhitehawk.com/ConfirmFriendRequest"
U_F_DEC    = "https://clientbp.ggwhitehawk.com/DeclineFriendRequest"

AID = "100067"

def gh(r: Request):
    ua = r.headers.get("user-agent", "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)")
    return {"User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip"}

def hs(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

@app.get("/")
async def home():
    return {"status": "SUCCESS", "msg": "SAMEER-API-V14-LIVE"}

# --- BINDING ---
@app.get("/api/request")
async def req_otp(token: str, email: str, request: Request):
    p = {"app_id": AID, "access_token": token, "email": email, "locale": "en_PK", "region": "PK"}
    r = requests.post(U_OTP, data=p, headers=gh(request))
    return r.json()

@app.get("/api/confirm")
async def confirm_bind(token: str, email: str, otp: str, request: Request):
    h = gh(request)
    v_res = requests.post(U_V_OTP, data={"app_id": AID, "access_token": token, "email": email, "otp": otp}, headers=h).json()
    vt = v_res.get("verifier_token")
    if not vt: return {"status": "ERROR", "msg": "OTP Verification Failed", "garena": v_res}
    
    # Logic for fresh account: set password 123456
    p = {"app_id": AID, "access_token": token, "verifier_token": vt, "email": email, "secondary_password": hs("123456")}
    r = requests.post(U_BIND, data=p, headers=h)
    return r.json()

# --- INFO & RANK ---
@app.get("/api/info")
async def get_info(token: str, request: Request):
    h = gh(request)
    b = requests.get(U_INFO, params={"app_id": AID, "access_token": token}, headers=h).json()
    uid = b.get("uid") or "0"
    r = requests.get(U_RANK, params={"access_token": token, "target_account_id": uid}, headers=h).json()
    return {"bind": b, "rank": r}

# --- FRIENDS ---
@app.get("/api/friends")
async def friends(token: str, mode: str, target: str = None, request: Request):
    h = gh(request)
    u_map = {"list": U_F_LIST, "add": U_F_ADD, "remove": U_F_REM, "accept": U_F_ACC, "decline": U_F_DEC}
    url = u_map.get(mode)
    if not url: return {"err": "Invalid mode"}
    p = {"access_token": token}
    if target: p["target_account_id"] = target
    r = requests.get(url, params=p, headers=h)
    return r.json()

@app.get("/api/cancel")
async def cancel(token: str, request: Request):
    return requests.post(U_CANCEL, data={"app_id": AID, "access_token": token}, headers=gh(request)).json()

# Vercel variable mapping
handler = app
