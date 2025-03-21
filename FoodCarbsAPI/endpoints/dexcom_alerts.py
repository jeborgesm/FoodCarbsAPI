import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get values from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

# Dexcom API endpoints
TOKEN_URL = 'https://sandbox-api.dexcom.com/v2/oauth2/token'
ALERTS_URL = 'https://sandbox-api.dexcom.com/v3/users/self/alerts'

def get_access_token(client_id, client_secret, refresh_token):
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
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    try:
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
        alerts = get_alerts(access_token)
        print(alerts)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

