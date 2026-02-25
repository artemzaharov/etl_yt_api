import requests
from dotenv import load_dotenv, dotenv_values

load_dotenv()
_env = dotenv_values()

YOUTUBE_KEY = _env.get('YOUTUBE_KEY')
YOUTUBE_CHANNEL = "3blue1brown"
MAX_RESULTS = 50

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



def get_video_ids(playlist_id):

    video_ids = []

    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={playlist_id}&key={YOUTUBE_KEY}"

    try:
        while True:
            url = base_url
            if pageToken:
                url += f"&pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            
            for item in data.get('items',[]):
                video_ids.append(item['contentDetails']['videoId'])

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    except requests.RequestException as e:
        return e


if __name__ == "__main__":
    playlist_id = get_channel_id()
    video_ids = get_video_ids(playlist_id)
    print(video_ids)