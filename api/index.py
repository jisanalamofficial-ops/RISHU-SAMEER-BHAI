import requests
import hashlib
from fastapi import FastAPI, Request

app = FastAPI()

# --- GARENA & SOCIAL FULL URLS (BD SERVER) ---
URL_BIND_INFO    = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
URL_SEND_OTP     = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
URL_VERIFY_OTP   = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
URL_BIND_REQ     = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
URL_VERIFY_ID    = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
URL_REBIND_REQ   = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
URL_CANCEL_REQ   = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
URL_PLATFORM     = "https://100067.connect.garena.com/bind/app/platform/info/get"
URL_LOGOUT       = "https://100067.connect.garena.com/oauth/logout"
# Social / Rank
URL_RANK_INFO    = "https://clientbp.ggwhitehawk.com/GetPlayerCSRankingInfoByAccountID"
URL_FRIEND_LIST  = "https://clientbp.ggwhitehawk.com/GetFriendRequestList"
URL_FRIEND_ADD   = "https://clientbp.ggwhitehawk.com/RequestAddingFriend"
URL_FRIEND_REM   = "https://clientbp.ggwhitehawk.com/RemoveFriend"
URL_FRIEND_ACC   = "https://clientbp.ggwhitehawk.com/ConfirmFriendRequest"
URL_FRIEND_DEC   = "https://clientbp.ggwhitehawk.com/DeclineFriendRequest"

AID = "100067"
SEC = "123456"

def get_h(r: Request):
    ua = r.headers.get("user-agent", "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)")
    return {"User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip"}

def hs(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

@app.get("/api")
async def home():
    return {"status": "SUCCESS", "msg": "Sameer Supreme V12 Live"}

# --- BINDING MODULE ---
@app.get("/api/request")
async def request_otp(token: str, email: str, request: Request):
    p = {"app_id": AID, "access_token": token, "email": email, "locale": "en_PK", "region": "PK"}
    r = requests.post(URL_SEND_OTP, data=p, headers=get_h(request))
    return r.json()

@app.get("/api/confirm")
async def confirm_bind(token: str, email: str, otp: str, request: Request):
    hdr = get_h(request)
    v_res = requests.post(URL_VERIFY_OTP, data={"app_id": AID, "access_token": token, "email": email, "otp": otp}, headers=hdr).json()
    vt = v_res.get("verifier_token")
    if not vt: return {"status": "FAIL", "msg": "OTP Invalid", "garena": v_res}
    
    # New Bind logic with Sec Code Injection
    p = {"app_id": AID, "access_token": token, "verifier_token": vt, "email": email, "secondary_password": hs(SEC)}
    r = requests.post(URL_BIND_REQ, data=p, headers=hdr)
    return r.json()

# --- INFO & RANK MODULE ---
@app.get("/api/info")
async def info(token: str, request: Request):
    hdr = get_h(request)
    b = requests.get(URL_BIND_INFO, params={"app_id": AID, "access_token": token}, headers=hdr).json()
    uid = b.get("uid") or "0"
    r = requests.get(URL_RANK_INFO, params={"access_token": token, "target_account_id": uid}, headers=hdr).json()
    return {"bind_data": b, "rank_data": r}

# --- FRIEND SYSTEM MODULE ---
@app.get("/api/friends")
async def friends_manager(token: str, mode: str, target: str = None, request: Request):
    hdr = get_h(request)
    u_map = {"list": URL_FRIEND_LIST, "add": URL_FRIEND_ADD, "remove": URL_FRIEND_REM, "accept": URL_FRIEND_ACC, "decline": URL_FRIEND_DEC}
    url = u_map.get(mode)
    p = {"access_token": token}
    if target: p["target_account_id"] = target
    return requests.get(url, params=p, headers=hdr).json()

# --- EXTRA UTILS ---
@app.get("/api/cancel")
async def cancel(token: str, request: Request):
    return requests.post(URL_CANCEL_REQ, data={"app_id": AID, "access_token": token}, headers=get_h(request)).json()

@app.get("/api/platform")
async def plat(token: str, request: Request):
    return requests.get(URL_PLATFORM, params={"access_token": token}, headers=get_h(request)).json()

@app.get("/api/revoke")
async def revoke(token: str, request: Request):
    r = requests.get(URL_LOGOUT, params={"access_token": token, "refresh_token": "1380dcb63ab3a077dc05bdf0b25ba4497c403a5b4eae96d7203010eafa6c83a8"}, headers=get_h(request))
    return {"status": "Logged Out", "res": r.text}
