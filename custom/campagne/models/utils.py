import os
from simple_salesforce import Salesforce
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

class sf_api:
    def get_access_token(self,login_url,client_id,client_secret):
        login_url = f'{login_url}/services/oauth2/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        }
        response = requests.post(login_url, data=data)
        return response.json().get("access_token"), response.json().get("instance_url")

    def __init__(self,mode):
        if mode == 'test':
            test_login_url = os.getenv('test_login_url')
            test_client_id = os.getenv('test_client_id')
            test_client_secret = os.getenv('test_client_secret')
            access_token,instance_url = self.get_access_token(test_login_url,test_client_id,test_client_secret)
            self.sf = Salesforce(instance_url=instance_url, session_id=access_token)
        elif mode == 'prod':
            prod_login_url = os.getenv('prod_login_url')
            prod_client_id = os.getenv('prod_client_id')
            prod_client_secret = os.getenv('prod_client_secret')
            access_token,instance_url = self.get_access_token(prod_login_url,prod_client_id,prod_client_secret)
            self.sf = Salesforce(instance_url=instance_url, session_id=access_token)
        else:
            raise Exception("Only test and prod are accepted!")