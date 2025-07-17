import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import os
import configparser

def login_task(request, username, password, remember=False):
    API_HOST = "http://192.168.1.91"
    API_GET = f"{API_HOST}/public_api/user/login"
    headers = {'Content-Type': 'application/json'}
    auth = (username, password)

    try:
        req = requests.get(API_GET, auth=auth, headers=headers)
        data = req.json() if req.headers.get("Content-Type","").startswith("application/json") else {}
        
        if req.status_code == 200 and data.get("error"):
            return JSONResponse(
                status_code=401,
                content={"mess": 0, "message": data["error"]}
            )
        if req.status_code == 200:
            # Tạo file config.ini sau khi đăng nhập thành công
            config_dir = r"C:\Users\Admin\AppData\Local\tnmhotmail"
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "config.ini")
            config = configparser.ConfigParser()
            config['login'] = {
                'remember': str(remember).lower(),
                'user': username if remember else '',
                'password': "password",
                'autologin': 'false'
            }
            with open(config_path, 'w') as configfile:
                config.write(configfile)
            return JSONResponse(
                content={
                    "mess": len(data),     
                    "message": "ok"
                }
            )
        return JSONResponse(
            status_code=req.status_code,
            content={"mess": 0, "message": "Login server error"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"mess": 0, "message": f"Connection error: {e}"}
        )
