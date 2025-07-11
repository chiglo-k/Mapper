import requests
import json
from fastapi import HTTPException


class DataSender:
    @staticmethod
    async def send_data(data: list, api_url: str, api_key: str):

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=json.dumps(data)
            )

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error sending data: {str(e)}")