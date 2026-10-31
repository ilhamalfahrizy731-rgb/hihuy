import time
import requests
from fastapi import FastAPI, HTTPException, Query
from mangum import Mangum

app = FastAPI(title="NGL Sender API", version="1.0.0")

# API Key rahasia sesuai permintaanmu
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
        "message": "NGL Sender API is running!",
        "usage": "/send?username=TARGET&pesan=PESANMU&jumlah=3&jeda=0&apikey=hammudhabibii_"
    }

@app.get("/send")
def send_messages(
    username: str = Query(..., description="Username NGL target"),
    pesan: str = Query(..., description="Pesan yang ingin dikirim"),
    jumlah: int = Query(1, ge=1, le=50, description="Jumlah pengiriman (maks 50 untuk mencegah timeout serverless)"),
    jeda: float = Query(0.5, ge=0, le=5, description="Jeda waktu antar pengiriman dalam detik (bisa 0 untuk tanpa jeda)"),
    apikey: str = Query(..., description="API Key autentikasi")
):
    # Validasi API Key
    if apikey != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="API Key salah atau tidak valid!")

    success_count = 0
    fail_count = 0
    details = []

    for i in range(1, jumlah + 1):
        is_success = send_ngl_message(username, pesan)
        if is_success:
            success_count += 1
            details.append({"index": i, "status": "success"})
        else:
            fail_count += 1
            details.append({"index": i, "status": "failed"})
        
        # Eksekusi jeda hanya jika jeda lebih besar dari 0 dan bukan iterasi terakhir
        if i < jumlah and jeda > 0:
            time.sleep(jeda)

    return {
        "status": "completed",
        "target": f"@{username}",
        "total_requested": jumlah,
        "success": success_count,
        "failed": fail_count,
        "delay_seconds": jeda,
        "details": details
    }

# Handler untuk Serverless (Vercel / Netlify)
handler = Mangum(app)