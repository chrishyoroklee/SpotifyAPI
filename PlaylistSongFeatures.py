from dotenv import load_dotenv
import os
import base64
from requests import post, get

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
    json_result = result.json()
    token = json_result["access_token"]
    return token

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    all_tracks = []

    # Initial request to get the first page of tracks
    try:
        response = get(url, headers=headers, params={"limit": 100})
        response.raise_for_status()

        playlist_data = response.json()
        tracks = playlist_data.get("items", [])

        # Add the first page of tracks to the overall list
        all_tracks.extend(tracks)

        # Check if there are more tracks (pagination)
        while playlist_data.get("next"):
            response = get(playlist_data["next"])
            response.raise_for_status()
            playlist_data = response.json()
            tracks = playlist_data.get("items", [])

            # Add the current page of tracks to the overall list
            all_tracks.extend(tracks)

        return all_tracks

    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
        return None

def get_audio_features_for_tracks(token, track_ids):
    url = "https://api.spotify.com/v1/audio-features"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "ids": ",".join(track_ids)
    }

    try:
        response = get(url, headers=headers, params=params)

        # Check if the response status code indicates success
        response.raise_for_status()

        # Parse the JSON response
        audio_features_data = response.json()

        # Extract audio features from the response
        audio_features = audio_features_data["audio_features"]

        return audio_features

    except Exception as e:
        print(f"Error fetching audio features: {e}")
        return None

def main():
    audio_features_data = []  # Initialize the variable as an empty list

    playlist_url = "https://open.spotify.com/playlist/239iOV14rR7rToh6Onkgi8?si=b8df4c6bc28d4458"
    playlist_id = playlist_url.split("/")[-1].split("?")[0]  # Extract playlist ID from the URL and remove query parameters
    
    if playlist_id:
        print("Playlist ID:", playlist_id)
        token = get_token()
        playlist_tracks = get_playlist_tracks(token, playlist_id)

        if playlist_tracks:
            audio_features_data = []  # List to store dictionaries for each song's audio features

            for idx, track in enumerate(playlist_tracks):
                track_name = track['track']['name']
                print(f"Track {idx + 1}: {track_name}")

            # Get track IDs for audio features request
            track_ids = [track['track']['id'] for track in playlist_tracks if track.get('track') and track['track'].get('id')]
            if track_ids:
                token = get_token()
                audio_features = get_audio_features_for_tracks(token, track_ids)

                if audio_features:
                    for idx, features in enumerate(audio_features):
                        track_name = playlist_tracks[idx]['track']['name']
                        # Create dictionary for each song's audio features
                        song_data = {
                            "songTitle": track_name,
                            "Acousticness": features['acousticness'],
                            "Danceability": features['danceability'],
                            "Duration": features['duration_ms'],
                            "Energy": features['energy'],
                            "Valence": features['valence'],
                            "Tempo": features['tempo'],
                            "Speechiness": features['speechiness'],
                            "Mode": features['mode'],
                            "Loudness": features['loudness'],
                            "Liveness": features['liveness'],
                            "Key": features['key'],
                            "Instrumentalness": features['instrumentalness'],
                            "Time Signature": features['time_signature']
                        }
                        # Append the dictionary to the list
                        audio_features_data.append(song_data)

            else:
                print("Failed to fetch audio features.")
        else:
            print("No valid track IDs found in the playlist.")
    else:
        print("Failed to fetch playlist tracks.")
    
    # Print the list of dictionaries (optional)
    print(audio_features_data)

if __name__ == "__main__":
    main()