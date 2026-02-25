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

def batch_list(video_id_list, batch_size):
    for video_id in range(0, len(video_id_list), batch_size):
        yield video_id_list[video_id:video_id + batch_size]


def extract_video_data(video_id_list):
    extracted_data = []

    def batch_list(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id:video_id + batch_size]
    
    "https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_id}&key={YOUTUBE_KEY}"

    try:
        for batch in batch_list(video_id_list, batch_size=MAX_RESULTS):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={YOUTUBE_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            for item in data.get('items',[]):
                video_id = item['id']
                snippet = item['snippet']
                content_details = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    'video_id': video_id,
                    'title': snippet['title'],
                    'published_at': snippet['publishedAt'],
                    'duration': content_details['duration'],
                    'view_count': statistics.get('viewCount', None),
                    'like_count': statistics.get('likeCount', None),
                    'comment_count': statistics.get('commentCount', None),
                }
                extracted_data.append(video_data)
        return extracted_data


    except requests.RequestException as e:
        return e
    
if __name__ == "__main__":
    playlist_id = get_channel_id()
    video_ids = get_video_ids(playlist_id)
    video_data = extract_video_data(video_ids)
    print(video_data)