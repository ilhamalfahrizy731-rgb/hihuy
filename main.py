from fastapi import FastAPI, HTTPException, Query
from mangum import Mangum
import requests
import time

app = FastAPI(title="NGL Sender API", version="1.0.0")

VALID_API_KEY = "hammudhabibii_"

def send_ngl_message(username: str, message: str) -> bool:
    url = "https://ngl.link/api/submit"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "Origin": "https://ngl.link",
        "Referer": f"https://ngl.link/{username}"
    }
    payload = {
        "username": username,
        "question": message,
        "deviceId": "b61d4a97-3f3c-42b7-a379-880c5547a468",
        "gameSlug": "",
        "referrer": ""
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "NGL Sender API is running smoothly!",
        "author": "hammudhabibii_",
        "endpoints": {
            "send_message": "/send?username=TARGET&pesan=PESAN&jumlah=5&jeda=0&apikey=hammudhabibii_",
            "check_account": "/check?username=TARGET&apikey=hammudhabibii_"
        }
    }

@app.get("/send")
def send_messages(
    username: str = Query(..., description="Username NGL target"),
    pesan: str = Query(..., description="Pesan yang ingin dikirim"),
    jumlah: int = Query(1, ge=1, le=100, description="Jumlah pengiriman (maks 100)"),
    jeda: float = Query(0, ge=0, le=5, description="Jeda waktu antar pengiriman dalam detik"),
    apikey: str = Query(..., description="API Key autentikasi")
):
    if apikey != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="API Key salah atau tidak valid!")

    success_count = 0
    fail_count = 0

    for i in range(1, jumlah + 1):
        if send_ngl_message(username, pesan):
            success_count += 1
        else:
            fail_count += 1
        
        if i < jumlah and jeda > 0:
            time.sleep(jeda)

    return {
        "status": "success",
        "creator": "hammudhabibii_",
        "data": {
            "target": f"@{username}",
            "total_sent": success_count,
            "total_failed": fail_count,
            "total_requested": jumlah,
            "delay": f"{jeda}s"
        }
    }

@app.get("/check")
def check_account(
    username: str = Query(..., description="Username NGL yang ingin dicek"),
    apikey: str = Query(..., description="API Key autentikasi")
):
    if apikey != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="API Key salah atau tidak valid!")

    profile_url = f"https://ngl.link/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(profile_url, headers=headers, timeout=10)
        
        # Jika status 200, berarti halaman profil NGL ditemukan/aktif
        if response.status_code == 200:
            # Cek apakah isi HTML mengindikasikan akun tidak ditemukan (biasanya NGL mengembalikan teks tertentu atau redirect)
            if "not found" in response.text.lower() or "page not found" in response.text.lower():
                is_active = False
            else:
                is_active = True
        else:
            is_active = False

        return {
            "status": "success",
            "creator": "hammudhabibii_",
            "data": {
                "username": f"@{username}",
                "is_active": is_active,
                "profile_url": profile_url,
                "note": "Total inbox bersifat privat dan memerlukan login dashboard NGL."
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)
