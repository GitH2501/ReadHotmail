
import requests
from fastapi.responses import JSONResponse, HTMLResponse
from models.account import Account
from api.HotmailAPI import HotmailAPI

account_model = Account()
hotmailAPI = HotmailAPI()


async def gettoken_profile_task(request):
    

    data = await request.json()
    profileCount = data.get('profileCount')
    ids = data.get('ids')
    result = checkTokenInAccount(ids)
    
    return JSONResponse(
        content={
            "status_code": 200,
            "data": result,
        }
    )



def checkTokenInAccount(ids):
    action_array = []
    if not ids:
        print("không có id")
        return []
    list_data_account = account_model.readAccountForMultiID(ids)
    if list_data_account:
        position = 0
        for row in list_data_account:
            id = row['ID']
            completed = row['completed']  # lấy đúng completed từ DB
            action_array.append({
                'position': position,
                'ID': id if not completed else "",
                'action': 'start' if not completed else '',
                'completed': completed,
            })
            position += 1

        return action_array
    else:
        print("không có list")
        action_array.append({
            'position': 0,
            'ID': "",
            'action': "",
        })
        return action_array    