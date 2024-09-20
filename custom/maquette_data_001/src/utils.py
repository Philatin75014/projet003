import os
from simple_salesforce import Salesforce
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

class sf_api:
    """
    A class to interact with Salesforce API.
    Methods
    -------
    get_access_token(login_url, client_id, client_secret)
        Retrieves the access token and instance URL from Salesforce.
    __init__()
        Initializes the Salesforce connection using environment variables for test mode.
    """
    def get_access_token(self, login_url, client_id, client_secret):
        login_url = f'{login_url}/services/oauth2/token'
        data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        }

         # Exécuter la requête POST
        response = requests.post(login_url, data=data)
    
        # Vérifier si la réponse est valide
        # if response.status_code != 200:
        #    print(f"Erreur HTTP {response.status_code}: {response.text}")
        #raise Exception(f"Erreur d'authentification : {response.text}")
    
    # Récupérer le token d'accès et l'URL de l'instance
        access_token = response.json().get("access_token")
        instance_url = response.json().get("instance_url")
    
        # Si l'un des deux est None, lever une exception
        #if not access_token or not instance_url:
        #    raise Exception(f"Access token ou instance URL manquant dans la réponse : {response.json()}")
        # Retourner les deux valeurs
        return access_token, instance_url

    def __init__(self):
        #if mode == 'test':
            test_login_url = os.getenv('test_login_url')
            test_client_id = os.getenv('test_client_id')
            test_client_secret = os.getenv('test_client_secret')
            # Vérifier que les variables sont correctement chargées
            print(os.getenv('test_login_url'))
            print(os.getenv('test_client_id'))
            print(os.getenv('test_client_secret'))
            access_token,instance_url = self.get_access_token(test_login_url,test_client_id,test_client_secret)
            self.sf = Salesforce(instance_url=instance_url, session_id=access_token)
        #elif mode == 'prod':
        #    prod_login_url = os.getenv('prod_login_url')
        #    prod_client_id = os.getenv('prod_client_id')
        #    prod_client_secret = os.getenv('prod_client_secret')
        #    access_token,instance_url = self.get_access_token(prod_login_url,prod_client_id,prod_client_secret)
        #    self.sf = Salesforce(instance_url=instance_url, session_id=access_token)
        #else:
        #    raise Exception("Only test and prod are accepted!")