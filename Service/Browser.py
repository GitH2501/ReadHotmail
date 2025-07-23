import re
import random
import json
import string
from playwright.sync_api import sync_playwright, Error as PlaywrightError
import time
import os
from threading import Thread
import asyncio
from playwright.async_api import async_playwright
import tempfile
import zipfile
from Service.Config import create_dir_path_save_profile, create_dir_path_save_extension
from Service.Bypass import bypass
# from Config import create_dir_path_save_profile, create_dir_path_save_extension
# from Bypass import bypass
import asyncio
import websockets

class BrowserContext:

    URLs = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=9e5f94bc-e8a4-4e73-b8be-63364c29d753&response_type=code&redirect_uri=https%3A%2F%2Flocalhost&scope=https%3A%2F%2Fgraph.microsoft.com%2FMail.Read+https%3A%2F%2Fgraph.microsoft.com%2FUser.Read+offline_access&response_mode=query"
    
    def __init__(self):
        self.last_url = None
        self.code_found = False
        self.auth_code = None
    
    def init_browser(self,data_profile):
        self.data_profile = data_profile
    
    def secure_random_string(self,length=64):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def generate_fingerprint(self):
        gpu_list = [
            "NVIDIA GeForce GTX 1050 Ti", "AMD Radeon RX 570", "Intel UHD Graphics 620",
            "Apple M1", "NVIDIA GeForce RTX 3080"
        ]
        memory_options = [4, 8, 16, 32]
        random.shuffle(gpu_list)

        # Tạo fingerprint mặc định nếu không có sẵn
        default_fp = {
            'GPU': random.choice(gpu_list),
            'Random': random.randint(1, 100),
            'R6408': random.randint(1000, 5000),
            'R35661': random.randint(1000, 5000),
            'R36349': random.randint(1000, 5000),
            'Device1': self.secure_random_string(32),
            'Device2': self.secure_random_string(32)
        }

        # Sử dụng fingerprint hiện có nếu có hoặc dùng mặc định
        if hasattr(self, 'fingerprint'):
            fp = self.data_profile
        else:
            fp = default_fp

        return {
            "webgl": {
                "GPU": fp.get('GPU', default_fp['GPU']),
                "Random": fp.get('Random', default_fp['Random']),
                "R6408": fp.get('R6408', default_fp['R6408']),
                "R35661": fp.get('R35661', default_fp['R35661']),
                "R36349": fp.get('R36349', default_fp['R36349']),
            },
            "device1": fp.get('Device1', default_fp['Device1']),
            "device2": fp.get('Device2', default_fp['Device2']),
            "navigator": {
                "vendorSub": "",
                "productSub": "20030107",
                "vendor": "Google Inc.",
                "maxTouchPoints": 0,
                "userActivation": {
                    "hasBeenActive": False,
                    "isActive": False,
                },
                "connection": {
                    "effectiveType": "4g",
                    "rtt": 100,
                    "downlink": 10.0,
                    "saveData": False,
                    "type": "wifi"
                },
                "hardwareConcurrency": 8,
                "cookieEnabled": True,
                "appCodeName": "Mozilla",
                "appName": "Netscape",
                "appVersion": "5.0 (Windows)",
                "platform": "Win32",
                "product": "Gecko",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "language": "en-US",
                "onLine": True,
                "mediaSession": {
                    "playbackState": "none"
                },
                "deviceMemory": random.choice(memory_options),
            }
        }

    def build_js_injection(self, fp_json: dict):
        bypass_js = bypass()
        return f"const DanaFP = {json.dumps(fp_json)};\n{bypass_js}"

    def parse_extension_dir(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_fill_info_ext = os.path.abspath(os.path.join(base_dir,"..", "extension", "fill_info_extension"))
        path_to_proxy_auth_ext = os.path.abspath(os.path.join(base_dir,"..", "extension", "proxy_auth_extension"))
        

        if not os.path.exists(path_to_fill_info_ext):
            print(f"File extension không tồn tại: {path_to_fill_info_ext}")
            return

        if not os.path.exists(path_to_proxy_auth_ext):
            print(f"File extension không tồn tại: {path_to_proxy_auth_ext}")
            return

        


        ext_path = f"{path_to_fill_info_ext},{path_to_proxy_auth_ext}"
        return ext_path

    def create_user_data_dir(self, id_profile):
        user_data_dir = create_dir_path_save_profile(id_profile)
        return user_data_dir
    def create_extension_dir(self, id_profile):
        user_data_dir = create_dir_path_save_profile(id_profile)
        extension_dir = os.path.join(user_data_dir, "profile",f'{id}')

    def run_browser(self):
        username = self.data_profile['Profile_name']
        password = self.data_profile['Password']
        browser_id = self.data_profile['Browser_id']
        profile_id = self.data_profile['ID']
        proxy_ip = self.data_profile['Proxy_ip']
        proxy_port = self.data_profile['Proxy_port']
        proxy_user = self.data_profile['Proxy_user']
        proxy_pass = self.data_profile['Proxy_pass']
        proxy_type = self.data_profile['Proxy_type'].lower()
         
        fp = self.generate_fingerprint()
        user_data_dir = self.create_user_data_dir(profile_id)
        ext_path = self.parse_extension_dir()
        # ext_path = f"C:\\Users\\NamVT\\AppData\\Local\\tnmhotmail\\profile\\99876\\proxy_auth_extension"


        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir,
                channel="chrome",
                headless=False,
                 args=[
                    f"--disable-extensions-except={ext_path}",
                    f"--load-extension={ext_path}",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    '--unsafely-treat-insecure-origin-as-secure=https://localhost',
                    "--disable-blink-features=AutomationControlled",  
                    "--exclude-switches=enable-automation",           
                    "--disable-automation",                                         
                    "--disable-infobars",                                    
                    "--disable-default-apps",                                        
                    "--no-first-run",                                         
                    "--no-default-browser-check",                                 
                    "--disable-backgrounding-occluded-windows",            
                    "--disable-renderer-backgrounding",                      
                    "--disable-background-timer-throttling",               
                    "--disable-features=TranslateUI",                            
                    "--disable-ipc-flooding-protection",                      
                    "--disable-hang-monitor",                               
                    "--disable-client-side-phishing-detection",                 
                    "--disable-popup-blocking",                               
                    "--disable-prompt-on-repost",                         
                    "--disable-sync",                                     
                    "--disable-domain-reliability",                             
                    "--disable-component-update",                              
                    "--disable-background-networking",                          
                    "--metrics-recording-only",                      
                    "--no-report-upload",                                  
                    "--no-pings",                                     
                    "--password-store=basic",                               
                    "--use-mock-keychain",                                 
                    "--mute-audio",                                     
                    "--remote-debugging-port=0",                                 
                    "--disable-logging",                                     
                    "--disable-gpu-sandbox",                             
                    "--disable-software-rasterizer",                            
                    "--disable-background-timer-throttling",                 
                    "--disable-features=VizDisplayCompositor,VizHitTestDrawQuad,TranslateUI",
                    "--aggressive-cache-discard",                  
                    "--disable-extensions-http-throttling",                       
                    "--disable-component-extensions-with-background-pages",
                    "--force-color-profile=srgb",                          
                    "--hide-scrollbars",                                   
                ],
                user_agent=fp["navigator"]["userAgent"],
                locale=fp["navigator"]["language"],
                java_script_enabled=True,
                accept_downloads=True,
                ignore_https_errors=True,
                bypass_csp=True,
            )


           
            # self.load_proxy_info(context, proxy_ip, proxy_port, proxy_user, proxy_pass, proxy_type)
            inject_js = self.build_js_injection(fp)
            context.add_init_script(inject_js)
            popup_page = context.new_page()
            popup_page.goto("http://127.0.0.1:8800/popup", wait_until="load")
            popup_page.evaluate(
                """({username, password, browser_id, profile_id}) => {
                    localStorage.setItem("username", username);
                    localStorage.setItem("password", password);
                    localStorage.setItem("browser_id", browser_id);
                    localStorage.setItem("profile_id", profile_id);

                }""",
                { "username": username, "password": password,  "browser_id":browser_id, "profile_id":profile_id}
            )


            page = context.new_page()
            if len(context.service_workers) == 0:
                print("Waiting for service worker...")
                try:
                    background = context.wait_for_event("serviceworker", timeout=60000)
                    print("Service worker ready:", background.url)
                except Exception as e:
                    print(f"Service worker timeout: {e}")
                    if len(context.background_pages) > 0:
                        background = context.background_pages[0]
                        print("Using background page instead:", background.url)
                    else:
                        print("No service worker or background page found")
                        return
            else:
                background = context.service_workers[0]
                print("Service worker already exists:", background.url)


            try:
                page.goto(self.URLs, wait_until="load")
                time.sleep(10)
                page.evaluate(
                """({username, password, browser_id, profile_id}) => {
                    localStorage.setItem("username", username);
                    localStorage.setItem("password", password);
                    localStorage.setItem("browser_id", browser_id);
                    localStorage.setItem("profile_id", profile_id);

                }""",
                { "username": username, "password": password,  "browser_id":browser_id, "profile_id":profile_id}
            )
            except Exception as a:
                print("lỗi rồi nhé",a)

            

            # page.reload()
            # time.sleep(15)
            
            is_stop = False
            while True:
                try:
                    page.evaluate("() => document.title")
                    time.sleep(1)
                except Exception as e:
                    error_msg = str(e).lower()

                    if "execution context was destroyed" in error_msg:
                        time.sleep(2)
                        continue
                    elif "target closed" in error_msg or "browser closed" in error_msg:
                        break
                    elif "page closed" in error_msg:
                        print("Page đã đóng!")
                        break
                    else:
                        is_stop = True
                        print(f"Lỗi khác: {e}")
                        time.sleep(1)
                        break

        return is_stop               


if __name__ == "__main__":
    b = BrowserContext()
    # b.init_browser(id_profile="12345", browser="chrome", fingerprint=None)
    # asyncio.run(b.run_browser())
    b.run_browser()
