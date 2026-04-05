from fastapi import FastAPI, Request
import requests
import hashlib

# Vercel entrypoint (Must be at the very top level)
app = FastAPI()

U1 = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
U2 = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
U3 = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
U4 = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
U5 = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
U6 = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
U7 = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
U8 = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
U9 = "https://100067.connect.garena.com/bind/app/platform/info/get"
U10 = "https://100067.connect.garena.com/oauth/logout"
U11 = "https://clientbp.ggwhitehawk.com/GetPlayerCSRankingInfoByAccountID"
U12 = "https://clientbp.ggwhitehawk.com/GetFriendRequestList"
U13 = "https://clientbp.ggwhitehawk.com/RequestAddingFriend"
U14 = "https://clientbp.ggwhitehawk.com/RemoveFriend"
U15 = "https://clientbp.ggwhitehawk.com/ConfirmFriendRequest"
U16 = "https://clientbp.ggwhitehawk.com/DeclineFriendRequest"
U17 = "https://100067.msdk.garena.com/api/msdk/v2/info/pricing"

def gh(r: Request):
    ua = r.headers.get("user-agent", "GarenaMSDK/4.0.39 (M2007J22C; Android 10; en; US;)")
    return {"User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip"}

def hs(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

@app.get("/")
async def root():
    return {"status": "SUCCESS", "msg": "Sameer API V13 Fixed"}

@app.get("/request")
async def req(token: str, email: str, request: Request):
    p = {"app_id": "100067", "access_token": token, "email": email, "locale": "en_PK", "region": "PK"}
    r = requests.post(U2, data=p, headers=gh(request))
    return r.json()

@app.get("/confirm")
async def b_new(token: str, email: str, otp: str, sc: str = "123456", request: Request):
    h = gh(request)
    v_res = requests.post(U3, data={"app_id": "100067", "access_token": token, "email": email, "otp": otp}, headers=h).json()
    vt = v_res.get("verifier_token")
    if not vt: return {"status": "ERROR", "res": v_res}
    p = {"app_id": "100067", "access_token": token, "verifier_token": vt, "email": email, "secondary_password": hs(sc)}
    r = requests.post(U4, data=p, headers=h)
    return r.json()

@app.get("/info")
async def info(token: str, request: Request):
    h = gh(request)
    b = requests.get(U1, params={"app_id": "100067", "access_token": token}, headers=h).json()
    uid = b.get("uid", "0")
    r = requests.get(U11, params={"access_token": token, "target_account_id": uid}, headers=h).json()
    return {"bind": b, "rank": r}

@app.get("/friends")
async def fr(token: str, mode: str, target: str = None, request: Request):
    h = gh(request)
    m_map = {"list": U12, "add": U13, "remove": U14, "accept": U15, "decline": U16}
    u = m_map.get(mode)
    p = {"access_token": token}
    if target: p["target_account_id"] = target
    return requests.get(u, params=p, headers=h).json()
