import os
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from dotenv import load_dotenv

# On charge les clés
load_dotenv()

# Connexion à Spotify
# Je le mets en variable globale pour ne pas avoir à le repasser partout
cid = os.getenv("SPOTIPY_CLIENT_ID")
secret = os.getenv("SPOTIPY_CLIENT_SECRET")

if not cid or not secret:
    print("Attention : Clés API manquantes dans le .env")

auth_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


def get_tracks_year(year):
    print(f"Récupération des titres pour {year}...")
    tracks_list = []

    # On récupère par paquets de 50
    # J'ai mis une limite à 1000 pour avoir assez de matière
    for offset in range(0, 1000, 50):
        try:
            results = sp.search(q=f'year:{year}', type='track', limit=50, offset=offset)
            items = results['tracks']['items']

            if len(items) == 0:
                break

            tracks_list.extend(items)
            # Petite pause pour ne pas spammer l'API
            time.sleep(0.1)

        except Exception as e:
            print(f"Erreur pendant la recherche : {e}")
            break

    return tracks_list


def process_year(year):
    # 1. Récupération
    raw_tracks = get_tracks_year(year)
    print(f" -> {len(raw_tracks)} titres trouvés pour {year}")

    # 2. On nettoie les données pour garder ce qui nous intéresse
    clean_data = []
    for t in raw_tracks:
        # Parfois il manque des infos, on vérifie
        if t and t.get('artists') and t.get('album'):
            clean_data.append({
                'track_id': t['id'],
                'track_name': t['name'],
                'artist_id': t['artists'][0]['id'],
                'artist_name': t['artists'][0]['name'],
                'album_name': t['album']['name'],
                'album_release_date': t['album']['release_date'],
                'duration_ms': t['duration_ms'],
                'track_popularity': t['popularity']
            })

    df = pd.DataFrame(clean_data)

    # 3. On garde les 200 meilleurs
    df_sorted = df.sort_values(by='track_popularity', ascending=False)
    df_top = df_sorted.head(200).copy()

    # 4. On va chercher les infos manquantes des artistes (Genres, Followers)
    # L'API search ne donne pas ça, il faut utiliser sp.artists()
    artist_ids = df_top['artist_id'].unique().tolist()

    genres_map = {}
    followers_map = {}
    pop_map = {}

    # On fait des paquets de 50 ID d'artistes
    for i in range(0, len(artist_ids), 50):
        chunk = artist_ids[i:i + 50]
        try:
            full_artists = sp.artists(chunk)['artists']
            for a in full_artists:
                genres_map[a['id']] = a['genres']
                followers_map[a['id']] = a['followers']['total']
                pop_map[a['id']] = a['popularity']
        except:
            print("Erreur sur un paquet d'artistes")

    # On remplit le dataframe avec map
    df_top['artist_genres'] = df_top['artist_id'].map(genres_map)
    df_top['artist_followers'] = df_top['artist_id'].map(followers_map)
    df_top['artist_popularity'] = df_top['artist_id'].map(pop_map)

    df_top['year'] = year

    return df_top


def run_collection():
    all_data = []
    # De 2020 à 2024 inclus
    for y in range(2020, 2025):
        df_y = process_year(y)
        all_data.append(df_y)

    final_df = pd.concat(all_data, ignore_index=True)
    return final_df