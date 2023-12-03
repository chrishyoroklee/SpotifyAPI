from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist with this name exists..")
        return None
    return json_result[0]

def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    params = {"include_groups": "album", "limit": 50}  # Limiting to albums only, maximum 50 albums
    result = get(url, headers=headers, params=params)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_tracks_in_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

# Get artist information and albums
token = get_token()
result = search_for_artist(token, "D'angelo")

if result:
    artist_id = result["id"]
    albums = get_albums_by_artist(token, artist_id)

    # Display a list of albums
    print("Albums by the artist:")
    for idx, album in enumerate(albums):
        print(f"{idx + 1}. {album['name']}")

    # Prompt the user to select an album
    selected_album_index = int(input("Enter the number of the album you want to explore: ")) - 1
    selected_album = albums[selected_album_index]
    album_id = selected_album["id"]

    # Get tracks in the selected album
    album_tracks = get_tracks_in_album(token, album_id)

    # Display tracks in the selected album
    print(f"Tracks in the album '{selected_album['name']}':")
    for idx, track in enumerate(album_tracks):
        print(f"{idx + 1}. {track['name']}")

    # Prompt the user to select a track
    selected_track_index = int(input("Enter the number of the track you want to get audio features for: ")) - 1
    selected_track = album_tracks[selected_track_index]
    track_name = selected_track['name']
    track_id = selected_track['id']

    def get_audio_features(token, track_id):
        url = f"https://api.spotify.com/v1/audio-features/{track_id}"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        
        try:
            result.raise_for_status()  # Raise HTTPError for bad requests
            json_result = result.json()

            # Extract desired audio features
            features = {
                "acousticness": json_result["acousticness"],
                "danceability": json_result["danceability"],
                "duration_ms": json_result["duration_ms"],
                "energy": json_result["energy"],
                "valence": json_result["valence"],
                "tempo": json_result["tempo"],
                "speechiness": json_result["speechiness"],
                "mode": json_result["mode"],
                "loudness": json_result["loudness"],
                "liveness": json_result["liveness"],
                "key": json_result["key"],
                "instrumentalness": json_result["instrumentalness"],
                "time_signature": json_result["time_signature"]
            }

            return features
        except Exception as e:
            print(f"Error while fetching audio features: {e}")
            return None

    # Get audio features for the selected track
    audio_features = get_audio_features(token, track_id)

    # Print audio features
    if audio_features:
        print(f"Audio Features for '{track_name}':")
        print(f"Acousticness: {audio_features['acousticness']}")
        print(f"Danceability: {audio_features['danceability']}")
        print(f"Duration: {audio_features['duration_ms']} ms")
        print(f"Energy: {audio_features['energy']}")
        print(f"Valence: {audio_features['valence']}")
        print(f"Tempo: {audio_features['tempo']}")
        print(f"Speechiness: {audio_features['speechiness']}")
        print(f"Mode: {audio_features['mode']}")
        print(f"Loudness: {audio_features['loudness']}")
        print(f"Liveness: {audio_features['liveness']}")
        print(f"Key: {audio_features['key']}")
        print(f"Instrumentalness: {audio_features['instrumentalness']}")
        print(f"Time Signature: {audio_features['time_signature']}")
else:
    print("Artist not found.")
