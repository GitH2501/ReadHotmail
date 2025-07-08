
import requests
from fastapi.responses import JSONResponse, HTMLResponse
from models.account import Account
from api.HotmailAPI import HotmailAPI

account_model = Account()
hotmailAPI = HotmailAPI()
action_array = []

async def gettoken_profile_task(request):
    

    data = await request.json()
    profileCount = data.get('profileCount')
    ids = data.get('ids')
    result = checkTokenInAccount(ids)
    
    print("Profile Count:", profileCount)
    print("ids", ids)
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = [executor.submit(checkTokenInAccount, data_hotmail_local) for i in range(profileCount)]
    #     for future in concurrent.futures.as_completed(futures):
    #         action_array.append(future.result())

    # print("Action array:", action_array)
    return JSONResponse(
        content={
            "status_code": 200,
            "data": result,
        }
    )



def checkTokenInAccount(ids):
    if not ids:
        print("Không có id nha pro")
        return []
    list_data_account = account_model.readAccountForMultiID(ids)

    print("list_data_account: ", list_data_account)


    if list_data_account:
        position = 0
        for row in list_data_account:
            access_token = row['Access_token']
            refresh_token = row['Refresh_token']
            status = row['Status']
            id = row['ID']
            if access_token and refresh_token and status.lower() == 'completed':
                print("có completed")
                action_array.append({
                    'position': position,
                    'ID': "",
                    'action': '',
                })
            else:
                print("không có completed")
                action_array.append({
                    'position': position,
                    'ID': id,
                    'action': 'start',
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