import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Optional
from api.HotmailAPI import HotmailAPI
from api import User
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ImportConfig

class EofficeAPI:

    API_HOST = "http://192.168.1.91"
    API_LOGIN = f"{API_HOST}/public_api/user/login"
    auth = ()
    header = {}
    user = User()
    
    def __init__(self, debug_mode=None):
        self.session = self._create_session()
        self.debug_mode = debug_mode if debug_mode is not None else ImportConfig.DEBUG_MODE
    
    def _create_session(self):
        """Create a session with connection pooling and retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=ImportConfig.API_MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy, 
            pool_connections=ImportConfig.POOL_CONNECTIONS, 
            pool_maxsize=ImportConfig.POOL_MAXSIZE
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()

    async def get_profile_for_id(self,id):
        """Async wrapper for sync method"""
        return self.get_profile_for_id_sync(id)
    
    def get_profile_for_id_sync(self, profile_id: str) -> Dict:
        """Synchronous version for better performance"""
        self.API_GET = f"{self.API_HOST}/public_api/kdp/accounts/info/{profile_id}"
        self.auth = (self.user._username,self.user._password)
        self.header = {
            'content-type':'application/json'
        }
        
        try:
            req = self.session.get(url=self.API_GET,auth=self.auth,headers=self.header, timeout=ImportConfig.API_TIMEOUT)
            
            if req.status_code == 200:
                data = req.json()
                return data
            else:
                if self.debug_mode and ImportConfig.SHOW_API_ERRORS:
                    print(f"Eoffice API error for {profile_id}: {req.status_code}")
                return {}
        except Exception as e:
            if self.debug_mode and ImportConfig.SHOW_API_ERRORS:
                print(f"Exception fetching eoffice info for {profile_id}: {e}")
            return {}
    
    def get_profile_batch(self, profile_ids: List[str]) -> Dict[str, Dict]:
        """Get profile info for multiple profile IDs in parallel"""
        results = {}
        
        def fetch_single(profile_id):
            try:
                data = self.get_profile_for_id_sync(profile_id)
                return profile_id, data
            except Exception as e:
                if self.debug_mode and ImportConfig.SHOW_API_ERRORS:
                    print(f"Error fetching eoffice info for {profile_id}: {e}")
                return profile_id, {}
        

        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=ImportConfig.MAX_WORKERS) as executor:
            future_to_id = {executor.submit(fetch_single, profile_id): profile_id for profile_id in profile_ids}
            
            for future in as_completed(future_to_id):
                try:
                    profile_id, data = future.result()
                    results[profile_id] = data
                except Exception as e:
                    profile_id = future_to_id[future]
                    if self.debug_mode and ImportConfig.SHOW_API_ERRORS:
                        print(f"Error processing eoffice profile {profile_id}: {e}")
                    results[profile_id] = {}
        
        return results

    def check_auth(self,username,password):

        auth = (username,password)
        headers = {
            'content-type':'application/json'
        }

        req = self.session.get(url=self.API_LOGIN,auth=auth,headers=headers, timeout=ImportConfig.API_TIMEOUT)

        return req

# account_profile = []  

# async def convert_list_of_dict_account(account_data):
#     hotmail_api = HotmailAPI()
#     id = account_data.get("id")
#     hotmail_data = await hotmail_api.get_hotmail_info_for_id(id)

#     access_token =  hotmail_data.get("access_token", "") if hotmail_data else ""
#     refresh_token = hotmail_data.get("refresh_token", "") if hotmail_data else ""
#     error = hotmail_data.get("error", "") if hotmail_data else ""
#     status = hotmail_data.get("status", "") if hotmail_data else ""
#     # for row in data:
#     account_profile.append(
#         {
#         "ID": account_data.get("id"),
#         "Profile_name":account_data.get("username"),
#         "Password": account_data.get("password"),
#         "Access_token": access_token,
#         "Refresh_token": refresh_token,
#         "error": error,
#         "Status": status,
#         "Browser_id": account_data.get("browser", {}).get("id"),
#         "Fingerprint_id": account_data.get("id"),
#         },
#     )
#     return account_profile


# browser_profile = []
# async def convert_list_of_dict_browser(browser_data):

#     # for row in data:
#     browser_profile.append(
#         {
#         "ID": browser_data.get("id"),
#         "Browser_type":browser_data.get("browser", {}).get("browser_type"),
#         "Proxy_type": browser_data.get("browser", {}).get("proxy_type"),
#         "Proxy_ip": browser_data.get("browser", {}).get("proxy_ip"),
#         "Proxy_port":browser_data.get("browser", {}).get("proxy_port"),
#         "Proxy_user":browser_data.get("browser", {}).get("proxy_user"),
#         "Proxy_pass":browser_data.get("browser", {}).get("proxy_pass"),
#         "Profile_name":browser_data.get("browser", {}).get("profile_name"),
#         "Fingerprint_id":"",
#         },
#     )
#     return browser_profile

# fingerprint_profile = []
# async def convert_list_of_dict_fingerprint(fingerprint_data):


#     finger_info__node = fingerprint_data.get("browser").get("finger_info")
#     # for row in data:
#     fingerprint_profile.append(
#         {
#         "ID": fingerprint_data.get("id"),
#         "Group1":finger_info__node.get("group1"),
#         "Group2": finger_info__node.get("group2"),
#         "Device1":finger_info__node.get("device1"),
#         "Device2":finger_info__node.get("device2"),
#         "Device3":finger_info__node.get("device3"),
#         "GPU":finger_info__node.get("DanaFP.webgl.GPU"),
#         "R6408":finger_info__node.get("DanaFP.webgl.R6408"),
#         "R35661":finger_info__node.get("DanaFP.webgl.R35661"),
#         "R36349":finger_info__node.get("DanaFP.webgl.R36349"),
#         "Random":finger_info__node.get("DanaFP.webgl.Random"),
#         "Browser_id":fingerprint_data.get("browser", {}).get("id"),
#         "Id_profile":fingerprint_data.get("id")
#         },
#     )
#     return fingerprint_profile