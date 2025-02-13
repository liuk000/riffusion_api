import os
import time
from pathlib import Path
import requests
from datetime import datetime
from riffusion_api import RiffusionAPI
from pydub import AudioSegment

# Funzione per leggere il contenuto di un file di testo
def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"ERROR: Impossibile leggere il file {file_path}.")
        print(e)
        raise

# Lettura del file "lyrics.txt"
lyrics_file_path = Path(__file__).resolve().parent / 'lyrics.txt'
custom_text = read_file(lyrics_file_path)

# Lettura del file "Genre.txt"
genre_file_path = Path(__file__).resolve().parent / 'Genre.txt'
music_style = read_file(genre_file_path)

print(f"DEBUG: Genere musicale letto da Genre.txt: {music_style}")

# Inizializzazione dell'API Riffusion
SB_API_AUTH_TOKEN= "base64-eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0ltdHBaQ0k2SW1aclQzQnNSMnQxWTA4MVkyMUJRaklpTENKMGVYQWlPaUpLVjFRaWZRLmV5SnBjM01pT2lKb2RIUndjem92TDJobmRIQjZkV3RsZW05a2VISm5iV1pvYkhaNUxuTjFjR0ZpWVhObExtTnZMMkYxZEdndmRqRWlMQ0p6ZFdJaU9pSXpZVGRsTWpOaFpTMHlOelUyTFRSbVltUXRZalEyTnkwelpXTmhPVGt3TlRjMU5tSWlMQ0poZFdRaU9pSmhkWFJvWlc1MGFXTmhkR1ZrSWl3aVpYaHdJam94TnpRd01EWXpPVEV3TENKcFlYUWlPakUzTXprME5Ua3hNVEFzSW1WdFlXbHNJam9pYlhWMWMyRXVZMjl0Y0dGdWVVQm5iV0ZwYkM1amIyMGlMQ0p3YUc5dVpTSTZJaUlzSW1Gd2NGOXRaWFJoWkdGMFlTSTZleUp3Y205MmFXUmxjaUk2SW1kdmIyZHNaU0lzSW5CeWIzWnBaR1Z5Y3lJNld5Sm5iMjluYkdVaVhYMHNJblZ6WlhKZmJXVjBZV1JoZEdFaU9uc2lZWFpoZEdGeVgzVnliQ0k2SW1oMGRIQnpPaTh2YkdnekxtZHZiMmRzWlhWelpYSmpiMjUwWlc1MExtTnZiUzloTDBGRFp6aHZZMHBUTlhGSGIxa3hWREJKV25sbFpqVmxSRFZGY1hsTVVYZHNXblIwT0RSMFRHaFZObFpzY1V4VU9VZFpNVkJHWXpGeFBYTTVOaTFqSWl3aVpXMWhhV3dpT2lKdGRYVnpZUzVqYjIxd1lXNTVRR2R0WVdsc0xtTnZiU0lzSW1WdFlXbHNYM1psY21sbWFXVmtJanAwY25WbExDSm1kV3hzWDI1aGJXVWlPaUpOVlZWVFFTQkRiMjF3WVc1NUlpd2lhWE56SWpvaWFIUjBjSE02THk5aFkyTnZkVzUwY3k1bmIyOW5iR1V1WTI5dElpd2libUZ0WlNJNklrMVZWVk5CSUVOdmJYQmhibmtpTENKd2FHOXVaVjkyWlhKcFptbGxaQ0k2Wm1Gc2MyVXNJbkJwWTNSMWNtVWlPaUpvZEhSd2N6b3ZMMnhvTXk1bmIyOW5iR1YxYzJWeVkyOXVkR1Z1ZEM1amIyMHZZUzlCUTJjNGIyTktVelZ4UjI5Wk1WUXdTVnA1WldZMVpVUTFSWEY1VEZGM2JGcDBkRGcwZEV4b1ZUWldiSEZNVkRsSFdURlFSbU14Y1Qxek9UWXRZeUlzSW5CeWIzWnBaR1Z5WDJsa0lqb2lNVEV4TkRJd09UQXdNakEzTkRBeU5qSTJNamN6SWl3aWMzVmlJam9pTVRFeE5ESXdPVEF3TWpBM05EQXlOakkyTWpjekluMHNJbkp2YkdVaU9pSmhkWFJvWlc1MGFXTmhkR1ZrSWl3aVlXRnNJam9pWVdGc01TSXNJbUZ0Y2lJNlczc2liV1YwYUc5a0lqb2liMkYxZEdnaUxDSjBhVzFsYzNSaGJYQWlPakUzTXprME5Ua3hNVEI5WFN3aWMyVnpjMmx2Ymw5cFpDSTZJamsyWW1Vek9XTmhMV0kyWXpjdE5EYzNNQzFoTlRreExUTXlOamMwWXpsa056VmxOaUlzSW1selgyRnViMjU1Ylc5MWN5STZabUZzYzJWOS5ZXzJ4MnpVQVJEQ3o2RDFMUUd2eGRjVDQteGNQdUxGbUZ1XzN1SVBFRXFBIiwidG9rZW5fdHlwZSI6ImJlYXJlciIsImV4cGlyZXNfaW4iOjYwNDgwMCwiZXhwaXJlc19hdCI6MTc0MDA2MzkxMCwicmVmcmVzaF90b2tlbiI6IlBZVTNNZWRDcXQwOFNlYzZDa083QWciLCJ1c2VyIjp7ImlkIjoiM2E3ZTIzYWUtMjc1Ni00ZmJkLWI0NjctM2VjYTk5MDU3NTZiIiwiYXVkIjoiYXV0aGVudGljYXRlZCIsInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiZW1haWwiOiJtdXVzYS5jb21wYW55QGdtYWlsLmNvbSIsImVtYWlsX2NvbmZpcm1lZF9hdCI6IjIwMjUtMDItMTNUMTU6MDU6MDkuOTUwMDgxWiIsInBob25lIjoiIiwiY29uZmlybWVkX2F0IjoiMjAyNS0wMi0xM1QxNTowNTowOS45NTAwODFaIiwibGFzdF9zaWduX2luX2F0IjoiMjAyNS0wMi0xM1QxNTowNToxMC42OTcyNzc1ODhaIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZ29vZ2xlIiwicHJvdmlkZXJzIjpbImdvb2dsZSJdfSwidXNlcl9tZXRhZGF0YSI6eyJhdmF0YXJfdXJsIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSlM1cUdvWTFUMElaeWVmNWVENUVxeUxRd2xadHQ4NHRMaFU2VmxxTFQ5R1kxUEZjMXE9czk2LWMiLCJlbWFpbCI6Im11dXNhLmNvbXBhbnlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6Ik1VVVNBIENvbXBhbnkiLCJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYW1lIjoiTVVVU0EgQ29tcGFueSIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0pTNXFHb1kxVDBJWnllZjVlRDVFcXlMUXdsWnR0ODR0TGhVNlZscUxUOUdZMVBGYzFxPXM5Ni1jIiwicHJvdmlkZXJfaWQiOiIxMTE0MjA5MDAyMDc0MDI2MjYyNzMiLCJzdWIiOiIxMTE0MjA5MDAyMDc0MDI2MjYyNzMifSwiaWRlbnRpdGllcyI6W3siaWRlbnRpdHlfaWQiOiI5NDUzZWI4Zi1hZDIxLTRkMGQtODRkMC1lNzEwNGI0ZDA3NzEiLCJpZCI6IjExMTQyMDkwMDIwNzQwMjYyNjI3MyIsInVzZXJfaWQiOiIzYTdlM"
print("DEBUG: Inizializzazione dell'API Riffusion...")
api = RiffusionAPI(sb_api_auth_tokens_0=SB_API_AUTH_TOKEN)
print("DEBUG: API inizializzata correttamente.")

# Generazione della traccia audio
prompt = custom_text
print("DEBUG: Avvio generazione della traccia con il prompt letto dal file.")
print("DEBUG: Prompt utilizzato:")
print(prompt)
print(f"DEBUG: Stile musicale scelto: {music_style}")

try:
    track = api.generate(prompt=prompt, music_style=music_style, output_file="song.mp3")
    print("DEBUG: Traccia generata con successo.")
except requests.exceptions.JSONDecodeError as e:
    print("DEBUG: Errore nel parsing del JSON durante la generazione della traccia.")
    if os.path.exists("song.mp3"):
        print("DEBUG: Il file 'song.mp3' esiste. Proseguo utilizzando DummyTrack.")
        track = DummyTrack(result_file_path="song.mp3", lyrics=prompt)
    else:
        print("ERROR: Il file 'song.mp3' non esiste. Impossibile proseguire.")
        raise e

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

# Post-elaborazione del file audio generato
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
