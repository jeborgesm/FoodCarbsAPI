import requests
from dotenv import load_dotenv
import os
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs

# Load environment variables from .env file
load_dotenv()

# Get values from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
REDIRECT_URI = os.getenv('REDIRECT_URI')
AUTHORIZATION_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/login'
TOKEN_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/token'
ALERTS_URL = 'https://sandbox-api.dexcom.com/v3/users/self/alerts'

def get_authorization_code():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'offline_access'
    }
    url = f"{AUTHORIZATION_URL}?{urlencode(params)}"
    webbrowser.open(url)
    redirect_response = input("Paste the full redirect URL here: ")
    parsed_url = urlparse(redirect_response)
    return parse_qs(parsed_url.query)['code'][0]

def get_access_token(client_id, client_secret, authorization_code):
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

def get_alerts(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(ALERTS_URL, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    try:
        authorization_code = get_authorization_code()
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, authorization_code)
        alerts = get_alerts(access_token)
        print(alerts)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


