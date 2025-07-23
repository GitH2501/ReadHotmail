import requests
from api.GraphAPI import GraphAPI
from fastapi.responses import HTMLResponse, JSONResponse
from api.HotmailAPI import HotmailAPI
from models.model import Model
graph_api = GraphAPI()
hotmail_api = HotmailAPI()
model = Model()

async def push_token_task(request):
    body = await request.json()
    code = body.get("code")
    profile_name = body.get("profile_name")
    password = body.get("password")
    browser_id = body.get("browser_id")
    profile_id = body.get("profile_id")
    error = None
    completed = True

    print(code)
    result_graph_api = graph_api.get_token_by_code(code)
    
    if result_graph_api:
        access_token = result_graph_api.get("access_token")
        refresh_token = result_graph_api.get("refresh_token")
        if access_token:
            payload = {
                "profile_name": profile_name,
                "password": password,
                "browser_id": browser_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "error": error,
                "completed": completed,
                "profile_id": profile_id
            }
            data_update = {
                "Access_token":access_token,
                "Refresh_token":refresh_token,
                "Error":error,
                "Completed":completed
            }
            model.updateDB("account", profile_id, data_update)
            result_push_token =  await pushTokenToHotmailDb(request, payload)

            if result_push_token:
                return JSONResponse(
                    content={
                        "success": True,
                        "message": "Token pushed successfully", 
                        }
                    )
            else:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "Token pushed Failed", 
                    })
    else: 
        return JSONResponse(
                    content={
                        "success": False,
                        "message": "Token pushed Failed", 
                    })


async def pushTokenToHotmailDb(request, payload):
    result_hotmail_api =  hotmail_api.create_hotmail_profile(payload)
    print(f"Result from Hotmail API: {result_hotmail_api}")
    return result_hotmail_api



