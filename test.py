import os
import time
from pathlib import Path
import requests
from datetime import datetime
from riffusion_api import RiffusionAPI
from pydub import AudioSegment

# ------------------------------------------------------------------------------
# Classe DummyTrack: utilizzata per proseguire il flusso se si verifica un errore
# di parsing JSON, ma il file "song.mp3" risulta comunque generato.
# ------------------------------------------------------------------------------
class DummyTrack:
    def __init__(self, result_file_path, lyrics):
        self.result_file_path = result_file_path
        self.lyrics = lyrics

# ------------------------------------------------------------------------------
# Monkey-Patching per il Debug: Modifichiamo il metodo json() di requests.Response
# per stampare il contenuto della risposta in caso di errore nel parsing del JSON.
# ------------------------------------------------------------------------------
original_json = requests.Response.json

def debug_json(self, **kwargs):
    try:
        # Prova a effettuare il parsing del JSON normalmente
        return original_json(self, **kwargs)
    except requests.exceptions.JSONDecodeError as e:
        # Se si verifica un errore, stampa il testo completo della risposta per il debug
        print("DEBUG: JSONDecodeError catturato durante il parsing della risposta.")
        print("DEBUG: Testo della risposta:")
        print(self.text)
        raise

# Sostituisci il metodo json() originale con quello di debug
requests.Response.json = debug_json

# ------------------------------------------------------------------------------
# Lettura del file "lyrics.txt"
# Il file si trova nella stessa cartella dello script
# ------------------------------------------------------------------------------
lyrics_file_path = Path(__file__).resolve().parent / 'lyrics.txt'
print(f"DEBUG: Lettura del file di testo da: {lyrics_file_path}")

try:
    with open(lyrics_file_path, 'r', encoding='utf-8') as f:
        custom_text = f.read()
    print("DEBUG: Lettura del file completata con successo.")
except Exception as e:
    print("ERROR: Impossibile leggere il file 'lyrics.txt'.")
    print(e)
    raise

# ------------------------------------------------------------------------------
# Inizializzazione dell'API Riffusion
# Inserisci qui il token ottenuto seguendo le istruzioni dal sito Riffusion.
# ------------------------------------------------------------------------------
SB_API_AUTH_TOKEN = ("base64-eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0ltdHBaQ0k2"
                       "SW1aclQzQnNSMnQxWTA4MVkyMUJRaklpTENKMGVYQWlPaUpLVjFRaWZRLmV5SnBj"
                       "M01pT2lKb2RIUndjem92TDJobmRIQjZkV3RsZW05a2VISm5iV1pvYkhaNUxuTjFj"
                       "R0ZpWVhObExtTnZMMkYxZEdndmRqRWlMQ0p6ZFdJaU9pSmtabUk0T1RJeFlpMWxaalUw"
                       "TFRRNE0yTXRZbVpoTkMxbVpXVTJPR1l5TldNMU5ESWlMQ0poZFdRaU9pSmhkWFJvWlc1"
                       "MGFXTmhkR1ZrSWl3aVpYaHdJam94TnpNNU9URXhNakkxTENKcFlYUWlPakUzTXprek1E"
                       "WTBNalVzSW1WdFlXbHNJam9pYkhWallXSmxjblJwYm1sc2RXTmhRR2R0WVdsc0xtTnZi"
                       "U0lzSW5Cb2IyNWxJam9pSWl3aVlYQndYMjFsZEdGa1lYUmhJanA3SW5CeWIzWnBaR1Z5"
                       "SWpvaVoyOXZaMnhsSWl3aWNISnZkbWxrWlhKeklqcGJJbWR2YjJkc1pTSmRmU3dpZFhO"
                       "bGNsOXRaWFJoWkdGMFlTSTZleUpoZG1GMFlYSmZkWEpzSWpvaWFIUjBjSE02THk5c2FE"
                       "TXVaMjl2WjJ4bGRYTmxjbU52Ym5SbGJuUXVZMjl0TDJFdlFVTm5PRzlqU21aRVVHWTNl"
                       "V2t6Um1KcGVXcExWRUl3VkRWUVpqWkVRM0U1WVdwQ1l6RkVObDlGVFhsUVdHcGlSVmxF"
                       "V1ZOQk9HNTBaejF6T1RZdFl5SXNJbVZ0WVdsc0lqb2liSFZqWVdKbGNuUnBibWxzZFdO"
                       "aFFHZHRZV2xzTG1OdmJTSXNJbVZ0WVdsc1gzWmxjbWxtYVdWa0lqcDBjblZsTENKbWRX"
                       "eHNYMjVoYldVaU9pSk1kV05oSUVKbGNuUnBibWtpTENKcGMzTWlPaUpvZEhSd2N6b3ZM"
                       "MkZqWTI5MWJuUnpMbWR2YjJkc1pTNWpiMjBpTENKdVlXMWxJam9pVEhWallTQkNaWEow"
                       "YVc1cElpd2ljR2h2Ym1WZmRtVnlhV1pwWldRaU9tWmhiSE5sTENKd2FXTjBkWEpsSWpv"
                       "aWFIUjBjSE02THk5c2FETXVaMjl2WjJ4bGRYTmxjbU52Ym5SbGJuUXVZMjl0TDJFdlFV"
                       "Tm5PRzlqU21aRVVHWTNlV2t6Um1KcGVXcExWRUl3VkRWUVpqWkVRM0U1WVdwQ1l6RkVO"
                       "bDlGVFhsUVdHcGlSVmxFV1ZOQk9HNTBaejF6T1RZdFl5SXNJbkJ5YjNacFpHVnlYMmxr"
                       "SWpvaU1UQTBNVGMzT1RrNU1UQTBNVEV4TVRrM09ESTVJaXdpYzNWaUlqb2lNVEEwTVRj"
                       "M09UazVNVEEwTVRFeE1UazNPREk1SW4wc0luSnZiR1VpT2lKaGRYUm9aVzUwYVdOaGRH"
                       "VmtJaXdpWVdGc0lqb2lZV0ZzTVNJc0ltRnRjaUk2VzNzaWJXVjBhRzlrSWpvaWIyRjFk"
                       "R2dpTENKMGFXMWxjM1JoYlhBaU9qRTNNemt6TURZME1qVjlYU3dpYzJWemMybHZibDlw"
                       "WkNJNkltSTNNekkyWVRBM0xUSTFNall0TkRSbE1pMDRPVFprTFdVelpHRXhPVFk1WmpN"
                       "eVpTSXNJbWx6WDJGdWIyNTViVzkxY3lJNlptRnNjMlY5LnJMU3I1YTdXSlJUZFlZVmJq"
                       "cDMxU3BLWkpqazhBVjBOTldWZnlvWWd1bW8i")
print("DEBUG: Inizializzazione dell'API Riffusion...")
api = RiffusionAPI(sb_api_auth_tokens_0=SB_API_AUTH_TOKEN)
print("DEBUG: API inizializzata correttamente.")

# ------------------------------------------------------------------------------
# Generazione della traccia audio
# Utilizziamo il contenuto del file "lyrics.txt" direttamente come prompt
# ------------------------------------------------------------------------------
# Assegniamo il contenuto letto come prompt
prompt = custom_text

print("DEBUG: Avvio generazione della traccia con il prompt letto dal file.")
print("DEBUG: Prompt utilizzato:")
print(prompt)

# Specifica lo stile musicale (modifica se necessario, es. "pop", "rock", "gitar", ecc.)
music_style = "pop"
print(f"DEBUG: Stile musicale scelto: {music_style}")

# Tentativo di generazione della traccia con gestione non fatale dell'errore JSON
try:
    track = api.generate(prompt=prompt, music_style=music_style, output_file="song.mp3")
    print("DEBUG: Traccia generata con successo.")
except requests.exceptions.JSONDecodeError as e:
    print("DEBUG: Errore nel parsing del JSON durante la generazione della traccia.")
    print("DEBUG: Verifico se il file di output 'song.mp3' è stato comunque generato.")
    if os.path.exists("song.mp3"):
        print("DEBUG: Il file 'song.mp3' esiste. Proseguo utilizzando DummyTrack.")
        track = DummyTrack(result_file_path="song.mp3", lyrics=prompt)
    else:
        print("ERROR: Il file 'song.mp3' non esiste. Impossibile proseguire.")
        raise e

# ------------------------------------------------------------------------------
# Funzione per scaricare il brano musicale
# Il nome del file finale sarà basato sull'orario, giorno e mese (formato HH_DD_MM.mp3)
# ------------------------------------------------------------------------------
def download_song(audio_segment, format="mp3"):
    # Ottiene la data e l'ora corrente nel formato desiderato
    filename = datetime.now().strftime("%H_%d_%m.") + format
    try:
        audio_segment.export(filename, format=format)
        print(f"DEBUG: Brano esportato con successo come: {filename}")
    except Exception as e:
        print("ERROR: Impossibile esportare il brano.")
        print(e)
        raise
    return filename

# ------------------------------------------------------------------------------
# Funzione per riprodurre il brano automaticamente con afplay (macOS)
# ------------------------------------------------------------------------------
def play_song(filename):
    print(f"DEBUG: Avvio riproduzione del brano con afplay: {filename}")
    # Esegue il comando afplay per riprodurre il file audio
    os.system(f'afplay "{filename}"')

# ------------------------------------------------------------------------------
# Post-elaborazione del file audio generato
# Carichiamo il file audio, lo adattiamo a 2 minuti e lo salviamo
# ------------------------------------------------------------------------------
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

# Imposta la durata target: 2 minuti (120000 millisecondi)
target_duration_ms = 2 * 60 * 1000  # 120000 ms
print(f"DEBUG: Durata target impostata a: {target_duration_ms} millisecondi.")

# Adattamento della durata: taglio se troppo lunga o aggiunta di silenzio se troppo corta
if len(song) > target_duration_ms:
    song_2min = song[:target_duration_ms]
    print("DEBUG: La traccia supera i 2 minuti. Effettuo il taglio.")
elif len(song) < target_duration_ms:
    silence_duration = target_duration_ms - len(song)
    silence = AudioSegment.silent(duration=silence_duration)
    song_2min = song + silence
    print("DEBUG: La traccia è inferiore a 2 minuti. Aggiungo silenzio per completare la durata.")
else:
    song_2min = song
    print("DEBUG: La traccia ha esattamente la durata target.")

# Utilizza la funzione download_song per esportare il file con il nome dinamico
downloaded_filename = download_song(song_2min, format="mp3")

# Riproduci il brano automaticamente utilizzando afplay
play_song(downloaded_filename)
