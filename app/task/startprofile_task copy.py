import requests
from models.model import Model
from models.account import Account
import time
import threading
from api.GraphAPI import GraphAPI
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
# from Backend.App.Browser.BrowserContext import BrowserContext
from models.fingerprint import Fingerprint
from models.browser import Browser
from Service.Browser import BrowserContext
from api.HotmailAPI import HotmailAPI
from fastapi.responses import JSONResponse, HTMLResponse
from models.model import Model


graph = GraphAPI()
account_local = Account()
executor = ThreadPoolExecutor(max_workers=5)
browser = BrowserContext()
fingerprint_model = Fingerprint()
browser_model = Browser()
hotmail_api = HotmailAPI()
model = Model()


async def startprofile_task(request):


    data = await request.json()
    id_profile = data.get('id_profile')

    print(f"Start profile with ID: {id_profile}")
    data_account_profile = account_local.readAccountForID(id_profile)
    future = executor.submit(workerStartProfile, data_account_profile)
    
    result = future.result()
    print(result)
    return JSONResponse(
        content={
            'position': result['position'],
            'ID': result['ID'],
            'action': result['action'],
            'access_token' : result['access_token']
            

        }
    )

def workerStartProfile(data_account_profile):
    ID = data_account_profile['ID']
    profile_name = data_account_profile['Profile_name']
    password = data_account_profile['Password']
    browser_id = data_account_profile['Browser_id']
    profile_id = data_account_profile['ID']



    # fingerprint_profile = fingerprint_model.readFingerprintForID(ID)
    # browser_profile = browser_model.readBrowserForID(ID)

    data_profile = model.getProfileID(ID)
    print(data_profile)


    browser.init_browser(data_profile)
    is_stop = browser.run_browser()
    if is_stop:
        data_profile_id = model.getProfileID(ID)
        position = 1
        if data_profile_id['Access_token'] != "null" and data_profile_id['Refresh_token'] != "null":
            return {
                'position': position,
                'ID': '',
                'action': '',
                'access_token':data_profile_id['Access_token'],
                'completed': True,
                'started_but_failed': False
            }
            
        else:
            return {
                'position': position,
                'ID': ID,
                'action': 'start',
                'access_token':'',
                'started_but_failed': False,
                'error': 'data_profile_id is None'
            }

    


    
        


    