from fastapi import FastAPI, Request
import requests
import hashlib

app = FastAPI()

# FULL URLS
U_INFO = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
U_OTP = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
U_VOTP = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
U_BREQ = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
U_VID = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
U_RREQ = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
U_UBREQ = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
U_CAN = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
U_PLAT = "https://100067.connect.garena.com/bind/app/platform/info/get"
U_RANK = "https://clientbp.ggwhitehawk.com/GetPlayerCSRankingInfoByAccountID"
U_FLIST = "https://clientbp.ggwhitehawk.com/GetFriendRequestList"
U_FADD = "https://clientbp.ggwhitehawk.com/RequestAddingFriend"
U_FREM = "https://clientbp.ggwhitehawk.com/RemoveFriend"
U_FACC = "https://clientbp.ggwhitehawk.com/ConfirmFriendRequest"
U_FDEC = "https://clientbp.ggwhitehawk.com/DeclineFriendRequest"

def gh(r: Request):
    ua = r.headers.get("user-agent", "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)")
    return {"User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip"}

def hs(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

@app.get("/")
async def root():
    return {"status": "SUCCESS", "msg": "Sameer Vercel API Live"}

@app.get("/api/request")
async def req_otp(token: str, email: str, request: Request):
    p = {"app_id": "100067", "access_token": token, "email": email, "locale": "en_PK", "region": "PK"}
    return requests.post(U_OTP, data=p, headers=gh(request)).json()

@app.get("/api/confirm-new")
async def b_new(token: str, email: str, otp: str, sc: str = "123456", request: Request):
    h = gh(request)
    v_res = requests.post(U_VOTP, data={"app_id": "100067", "access_token": token, "email": email, "otp": otp}, headers=h).json()
    vt = v_res.get("verifier_token")
    if not vt: return {"status": "FAIL", "res": v_res}
    p = {"app_id": "100067", "access_token": token, "verifier_token": vt, "email": email, "secondary_password": hs(sc)}
    return requests.post(U_BREQ, data=p, headers=h).json()

@app.get("/api/rebind")
async def b_re(token: str, email: str, otp: str, sc: str, request: Request):
    h = gh(request)
    v = requests.post(U_VOTP, data={"app_id": "100067", "access_token": token, "email": email, "otp": otp}, headers=h).json()
    i = requests.post(U_VID, data={"app_id": "100067", "access_token": token, "secondary_password": hs(sc)}, headers=h).json()
    vt, it = v.get("verifier_token"), i.get("identity_token")
    if not vt or not it: return {"status": "FAIL", "vt": v, "it": i}
    p = {"app_id": "100067", "access_token": token, "identity_token": it, "verifier_token": vt, "email": email}
    return requests.post(U_RREQ, data=p, headers=h).json()

@app.get("/api/info")
async def get_info(token: str, request: Request):
    h = gh(request)
    b = requests.get(U_INFO, params={"app_id": "100067", "access_token": token}, headers=h).json()
    uid = b.get("uid", "0")
    r = requests.get(U_RANK, params={"access_token": token, "target_account_id": uid}, headers=h).json()
    return {"bind": b, "rank": r}

@app.get("/api/friends")
async def fr_mg(token: str, mode: str, target: str = None, request: Request):
    h = gh(request)
    m_map = {"list": U_FLIST, "add": U_FADD, "remove": U_FREM, "accept": U_FACC, "decline": U_FDEC}
    url = m_map.get(mode)
    p = {"access_token": token}
    if target: p["target_account_id"] = target
    return requests.get(url, params=p, headers=h).json()

@app.get("/api/cancel")
async def cancel(token: str, request: Request):
    return requests.post(U_CAN, data={"app_id": "100067", "access_token": token}, headers=gh(request)).json()
