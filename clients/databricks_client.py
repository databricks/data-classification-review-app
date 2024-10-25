import requests

def get_oauth_token(token_url, client_id, client_secret):
    # Prepare the request payload
    payload = {
        'grant_type': "client_credentials",
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'all-apis'
    }

    try:
        # Send the POST request to the token endpoint
        response = requests.post(token_url, data=payload)

        # Raise exception for HTTP errors
        response.raise_for_status()

        # Parse the response JSON to get the access token
        token_data = response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            raise Exception(f"Failed to retrieve access token: {token_data}")

        return access_token

    except requests.exceptions.RequestException as e:
        print(f"Failed to get OAuth token: {e}")
        return None

def make_authenticated_request(url, token_url, client_id, client_secret):
    # Get the OAuth token
    token = get_oauth_token(token_url, client_id, client_secret)

    if not token:
        raise Exception("Failed to obtain access token.")

    # Set the headers with Bearer token
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    try:
        # Send the POST request with data and headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception if the status code is not 200-299

        return response.json()  # Return the JSON response

    except requests.exceptions.RequestException as e:
        print(f"Failed to make POST request: {e}")
        return None