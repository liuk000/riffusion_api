import os
import time
from pathlib import Path
import requests
from datetime import datetime
from riffusion_api import RiffusionAPI
from pydub import AudioSegment

# Funzione per leggere il contenuto di un file di testo solo se modificato dopo l'apertura del codice
def read_file_if_modified(file_path, initial_mod_time):
    try:
        current_mod_time = os.path.getmtime(file_path)
        if current_mod_time > initial_mod_time:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip(), current_mod_time
        return None, initial_mod_time
    except Exception as e:
        print(f"ERROR: Impossibile leggere il file {file_path}.")
        print(e)
        return None, initial_mod_time

# Funzione per scaricare il brano musicale
def download_song(audio_segment, format="mp3"):
    filename = datetime.now().strftime("%H_%d_%m.") + format
    try:
        audio_segment.export(filename, format=format)
        print(f"DEBUG: Brano esportato con successo come: {filename}")
    except Exception as e:
        print("ERROR: Impossibile esportare il brano.")
        print(e)
        raise
    return filename

# Funzione per riprodurre il brano automaticamente su macOS
def play_song(filename):
    print(f"DEBUG: Avvio riproduzione del brano con afplay: {filename}")
    os.system(f'afplay "{filename}"')

# Percorsi dei file
lyrics_file_path = Path(__file__).resolve().parent / 'lyrics.txt'
genre_file_path = Path(__file__).resolve().parent / 'Genre.txt'

# Inizializza i timestamp di modifica iniziali
lyrics_mod_time = os.path.getmtime(lyrics_file_path)
genre_mod_time = os.path.getmtime(genre_file_path)

# Lettura iniziale del file "Genre.txt"
music_style, _ = read_file_if_modified(genre_file_path, genre_mod_time)
if music_style is None:
    music_style = "default"
print(f"DEBUG: Genere musicale letto da Genre.txt: {music_style}")

# Inizializzazione dell'API Riffusion
SB_API_AUTH_TOKEN = "<INSERISCI_IL_TUO_TOKEN>"
print("DEBUG: Inizializzazione dell'API Riffusion...")
api = RiffusionAPI(sb_api_auth_tokens_0=SB_API_AUTH_TOKEN)
print("DEBUG: API inizializzata correttamente.")

# Loop di controllo per verificare modifiche a "lyrics.txt"
custom_text = None
while True:
    updated_text, lyrics_mod_time = read_file_if_modified(lyrics_file_path, lyrics_mod_time)
    if updated_text is not None:
        custom_text = updated_text
        print("DEBUG: Testo modificato rilevato. Nuovo prompt aggiornato.")
    
    if custom_text:
        print("DEBUG: Avvio generazione della traccia con il prompt letto dal file.")
        print("DEBUG: Prompt utilizzato:")
        print(custom_text)
        print(f"DEBUG: Stile musicale scelto: {music_style}")

        try:
            track = api.generate(prompt=custom_text, music_style=music_style, output_file="song.mp3")
            print("DEBUG: Traccia generata con successo.")
        except requests.exceptions.JSONDecodeError as e:
            print("DEBUG: Errore nel parsing del JSON durante la generazione della traccia.")
            if os.path.exists("song.mp3"):
                print("DEBUG: Il file 'song.mp3' esiste. Proseguo utilizzando DummyTrack.")
                track = DummyTrack(result_file_path="song.mp3", lyrics=custom_text)
            else:
                print("ERROR: Il file 'song.mp3' non esiste. Impossibile proseguire.")
                raise e

        # Post-elaborazione del file audio
        print("DEBUG: Avvio post-elaborazione della traccia audio.")
        print("DEBUG: Testo generato:")
        print(track.lyrics)
        print("DEBUG: File audio generato:", track.result_file_path)

        try:
            song = AudioSegment.from_file(track.result_file_path, format="mp3")
            print("DEBUG: File audio caricato correttamente.")
        except Exception as e:
            print("ERROR: Impossibile caricare il file audio. Dettagli:")
            print(e)
            raise

        # Imposta la durata target: 2 minuti
        target_duration_ms = 2 * 60 * 1000  # 120000 ms
        if len(song) > target_duration_ms:
            song_2min = song[:target_duration_ms]
            print("DEBUG: La traccia supera i 2 minuti. Effettuo il taglio.")
        elif len(song) < target_duration_ms:
            silence_duration = target_duration_ms - len(song)
            silence = AudioSegment.silent(duration=silence_duration)
            song_2min = song + silence
            print("DEBUG: La traccia è inferiore a 2 minuti. Aggiungo silenzio.")
        else:
            song_2min = song
            print("DEBUG: La traccia ha esattamente la durata target.")

        # Esporta e riproduce il brano
        downloaded_filename = download_song(song_2min, format="mp3")
        play_song(downloaded_filename)
    
    time.sleep(2)  # Controlla ogni 2 secondi se "lyrics.txt" è stato modificato
