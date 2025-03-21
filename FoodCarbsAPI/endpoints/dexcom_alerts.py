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

def get_tokens(client_id, client_secret, authorization_code):
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    tokens = response.json()
    return tokens['access_token'], tokens['refresh_token']

def refresh_access_token(client_id, client_secret, refresh_token):
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

def get_alerts(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(ALERTS_URL, headers=headers)
    if response.status_code == 401:
        raise requests.exceptions.RequestException("Access token expired")
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    try:
        authorization_code = get_authorization_code()
        access_token, refresh_token = get_tokens(CLIENT_ID, CLIENT_SECRET, authorization_code)
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")
        
        try:
            alerts = get_alerts(access_token)
        except requests.exceptions.RequestException as e:
            if "Access token expired" in str(e):
                access_token = refresh_access_token(CLIENT_ID, CLIENT_SECRET, refresh_token)
                alerts = get_alerts(access_token)
            else:
                raise e
        
        print(alerts)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
