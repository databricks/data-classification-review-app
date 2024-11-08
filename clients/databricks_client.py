import requests
import time
import os


class DatabricksClient:
    def __init__(self, logger):
        self._logger = logger
        self._client_id = os.getenv("DATABRICKS_CLIENT_ID")
        self._client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
        self._host = "https://" + os.getenv("DATABRICKS_HOST")
        self._token_url = self._host + "/oidc/v1/token"

    def apply_review_results(
        self,
        table_name,
        accepted_classifications,
        rejected_classifications,
        token=None,
        token_expiration=None,
    ):
        json_data = {
            "accepted_classifications": accepted_classifications,
            "rejected_classifications": rejected_classifications,
        }

        return self._make_authenticated_request(
            f"/api/2.0/data-classification/tables/{table_name}/apply-review-results",
            json_data,
            token,
            token_expiration,
        )

    def _get_oauth_token(self):
        self._logger.info("Refreshing oauth token..")
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "all-apis",
        }
        response = requests.post(self._token_url, data=payload)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the response JSON to get the access token and expiration
        token_data = response.json()
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in")  # Token validity duration in seconds

        if not access_token or not expires_in:
            raise Exception(
                f"Failed to retrieve access token or expiration: {token_data}"
            )

        token_expiration = time.time() + int(expires_in)

        return (access_token, token_expiration)

    def _make_authenticated_request(
        self, url, json_data, oauth_token=None, token_expiration=None
    ):
        start_time = time.time()
        if (
            oauth_token is None
            or token_expiration is None
            or time.time() >= token_expiration
        ):
            token, token_expiration = self._get_oauth_token()
            if not token:
                raise Exception("Failed to obtain access token.")
        else:
            token = oauth_token

        # Set the headers with the Bearer token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        self._logger.info(f"Making request with data: {json_data}")

        full_url = self._host + url

        response = requests.post(full_url, headers=headers, json=json_data)

        if response.status_code == 401:
            # Token might have expired; try to get a new one and retry
            token, token_expiration = self._get_oauth_token()
            if not token:
                raise Exception("Failed to obtain access token.")
            headers["Authorization"] = f"Bearer {token}"
            response = requests.post(full_url, headers=headers, json=json_data)

        if not response.ok:
            # Try to extract error message from the response
            try:
                error_info = response.json()
                error_code = error_info.get("error_code", "Unknown")
                error_message = error_info.get("message", "No error message provided.")
                full_error_message = f"[{error_code}]: {error_message}"
            except ValueError:
                # Response content is not JSON
                full_error_message = f"Error {response.status_code}: {response.text}"
            # Log the full response for debugging
            self._logger.error(
                f"Request to {full_url} failed. Status code: {response.status_code}. Response: {response.text}"
            )
            raise Exception(full_error_message)

        end_time = time.time()
        elapsed_time = end_time - start_time
        self._logger.info(f"Apply review results api took {elapsed_time} seconds")
        return (response.json(), token, token_expiration)
