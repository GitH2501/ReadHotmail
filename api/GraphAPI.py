
import requests
import sys
import os
# from helper import write_ggsheet
# Thêm thư mục gốc vào sys.path để Python có thể tìm thấy module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class GraphAPI:

    _client_id = ""
    _grant_type = ""
    _redirect_uri = ""
    _url = ""
    header = {}
    body = {}
    
    # def __init__(self,code):
    #     self.code = code


    def get_token_for_code(self,code):

        self._client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
        self._grant_type = "authorization_code"
        self._redirect_uri = "https://localhost"
        self._url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.code = code

        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.body = {
            'client_id': self._client_id,
            'grant_type': self._grant_type,
            'redirect_uri': self._redirect_uri,
            'code':self.code
        }

        req = requests.post(url=self._url,data=self.body,headers=self.header)

        if req.status_code == 200:
            data = req.json()
        else:
            data = {}

        return data
    
    def refresh_token(self,refresh_token):
        self._client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
        self._grant_type = "refresh_token"
        self._redirect_uri = "https://localhost"
        self._url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self._refresh_token = refresh_token
        self._scope = "https://graph.microsoft.com/.default"

        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.body = {
            'client_id': self._client_id,
            'grant_type': self._grant_type,
            'redirect_uri': self._redirect_uri,
            'refresh_token':self._refresh_token,
            'scope':self._scope
        }

        req = requests.post(url=self._url,data=self.body,headers=self.header)

        if req.status_code == 200:
            data = req.json()
        else:
            data = {}

        return data
    def check_expire_access_token(self,access_token):
        pass

    def post_token(self,ROW_NUMBER,POSITION_COLUMN, SHEET):
        data = self.get_token()
        pair_column_value = {
            "ACCESS_TOKEN":data['access_token'],
            "REFRESH_TOKEN":data['refresh_token'],
            "Status": "DONE"
        }
        # write_ggsheet(row_number=ROW_NUMBER, pair_column_value=pair_column_value,
        #                 POSITION_COLUMN=POSITION_COLUMN, sheet=SHEET)
    def get_list_hotmail(self,access_token):
        graph_url = "https://graph.microsoft.com/v1.0/me/messages?$top=10&$orderby=receivedDateTime desc"
        is_expired = False

        self.header = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        mail_response = requests.get(graph_url, headers=self.header)

        if mail_response.status_code == 200:
            return is_expired,mail_response.json()
        elif mail_response.status_code == 401:
            is_expired = True
            return is_expired,{}
        else:
            is_expired = True
            return is_expired,{}
        

if __name__ == '__main__':
    access_token = "EwA4BMl6BAAUBKgm8k1UswUNwklmy2v7U/S+1fEAAW2YAmdKrnUqO3B3RYzE+RSihYE/SurYipkNqrYnjBRQaE2Rhy7SVkwAu36jqh5dNPnB0QagKNAbR/fMDWJgrxgW79dmaEFSzZKnc2cyicW4xCwoj/nc7gIA1AUgWCDi07y6UKep4jACpjQmx34S7/yo28xCw8E2CWO4g8RAB7pVloZVxaEDgQyTtOmx/FJtSUUTbgWZf7126jR+1S18d0VCV/dY6JLb5Ir6pP/KGHcnHwRR40+8QZiG7GoRdrcEYXaM81j17Fi4lZGzBEGek2/KhNkLraza4tE9JzaNMU0d6bVLdjmsvL/QPmlrwPsSYlOjjzP94JRXA374avbXxJMQZgAAEMRfjUkR4Cj49p8n9BQAX08AA6PmtitMah8dGK2LGdzmFav/TqgA5LRUUrsX4Z6QMwZo9W6Cvsxa5ONQmV6xLFpexmi0yY0yvDLmtIv/6YquOig41GNrRHqLnyBjFQg98nczilY0JljnHBhj+A8cgU+BQZsCjbG8FM4p18u72Jl9fe2lvGI1PtNnPiZu2t73ztBiaRMDRHiFupZCROnAOsOqRqRAnv9KLJR4zMT4I5n/DtANqoGzxE9HcTcB6UtZfSEgNSSC8nkWFiYyPMkrbHRRa7q3znXb7uqlOjsEP3ZbwOWsLZICwZtdO6wnyi1le0b2j9B2uvpOX8KxMM2+jF5/ErhxSCc60d4mt2fBIHpe/BvDZppSuw//e8OHjEvagMUFmdhTVE0euNpfsZnzbmDmLaetCxtJZZM5i0Tng8HCLTV1kFG+cA4UQTrEhrz5RG/5Hrm1jP2w6fnI0OFQyu6KfKzkvUQrM8/kKILhOHABgitoyZazLqWhQ9Zf3+jCPt1dLWvVsauuNXVVNheg9+h0SXA2nmR2P4KJ5USdKhLDZBYahamTot1S+LGsj0KdEsoLH0zJG8X239CeRGzl1iNXEsDOlxIMOtsuOrZ3rxdyxNQAjr9cuGad4GwkPoustEwD4P2VWsmdtcztOEK6jw4pRY5yzm31q2/MRZQElh6tYXKh1IxEBV9LhTaa1QneyFLuWUwjGclj31IrPFEk22j27jKE7q7wUtmE45zzz9w7mcA1po9cTD50FPFDfOoA9afUPDBcFylNEdmSLbnikT0TJrbddxpCRwJJQBgbDrO/Ik+W0eINVXXIv8kc2FI5fJLob8PWLIv534bpJnjVNizj7UlvmjewniYALqDu0/MDpfgKm+9R9uxOjuS1ijnWOC7swGfEsxF8bMwRAiUjqa7kcplImsvkdLIgxfSGJX93qDdLfhbYG5wzak4driRP6IR7KZgG3sbM/c5S1aKDdhLGN4RaqhBE4WRpWlpfBiWDnGJcDpMPu5FkW2Nj/ADOvMfeMWmyZeF5JTkJ8F+jXKOp+0ID"
    print(GraphAPI().get_list_hotmail(access_token))