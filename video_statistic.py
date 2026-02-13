import requests
import os
import json

YOUTUBE_KEY = os.getenv('YOUTUBE_KEY')
YOUTUBE_CHANNEL = "3blue1brown"

def get_channel_id():

    url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={YOUTUBE_CHANNEL}&key={YOUTUBE_KEY}' 

    try:
        response = requests.get(url)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx

        data = response.json()
        channel_data = data['items'][0]
        channel_items = channel_data['contentDetails']['relatedPlaylists']['uploads']

        return channel_items

    except requests.RequestException as e:
        raise RuntimeError(f"YouTube API request failed: {e}") from e
    except (KeyError, IndexError) as e:
        raise ValueError(f"Unexpected API response structure: {e}") from e


if __name__ == "__main__":
    get_channel_id()