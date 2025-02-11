import os
import time
from pathlib import Path
import requests
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
SB_API_AUTH_TOKEN = ("base64-eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0ltdHBaQ0k2SW1aclQzQnNSMnQxWTA4MVkyMUJRaklpTENKMGVYQWlPaUpLVjFRaWZRLmV5SnBjM01pT2lKb2RIUndjem92TDJobmRIQjZkV3RsZW05a2VISm5iV1pvYkhaNUxuTjFjR0ZpWVhObExtTnZMMkYxZEdndmRqRWlMQ0p6ZFdJaU9pSmtabUk0T1RJeFlpMWxaalUwTFRRNE0yTXRZbVpoTkMxbVpXVTJPR1l5TldNMU5ESWlMQ0poZFdRaU9pSmhkWFJvWlc1MGFXTmhkR1ZrSWl3aVpYaHdJam94TnpNNU9URXhNakkxTENKcFlYUWlPakUzTXprek1EWTBNalVzSW1WdFlXbHNJam9pYkhWallXSmxjblJwYm1sc2RXTmhRR2R0WVdsc0xtTnZiU0lzSW5Cb2IyNWxJam9pSWl3aVlYQndYMjFsZEdGa1lYUmhJanA3SW5CeWIzWnBaR1Z5SWpvaVoyOXZaMnhsSWl3aWNISnZkbWxrWlhKeklqcGJJbWR2YjJkc1pTSmRmU3dpZFhObGNsOXRaWFJoWkdGMFlTSTZleUpoZG1GMFlYSmZkWEpzSWpvaWFIUjBjSE02THk5c2FETXVaMjl2WjJ4bGRYTmxjbU52Ym5SbGJuUXVZMjl0TDJFdlFVTm5PRzlqU21aRVVHWTNlV2t6Um1KcGVXcExWRUl3VkRWUVpqWkVRM0U1WVdwQ1l6RkVObDlGVFhsUVdHcGlSVmxFV1ZOQk9HNTBaejF6T1RZdFl5SXNJbVZ0WVdsc0lqb2liSFZqWVdKbGNuUnBibWxzZFdOaFFHZHRZV2xzTG1OdmJTSXNJbVZ0WVdsc1gzWmxjbWxtYVdWa0lqcDBjblZsTENKbWRXeHNYMjVoYldVaU9pSk1kV05oSUVKbGNuUnBibWtpTENKcGMzTWlPaUpvZEhSd2N6b3ZMMkZqWTI5MWJuUnpMbWR2YjJkc1pTNWpiMjBpTENKdVlXMWxJam9pVEhWallTQkNaWEowYVc1cElpd2ljR2h2Ym1WZmRtVnlhV1pwWldRaU9tWmhiSE5sTENKd2FXTjBkWEpsSWpvaWFIUjBjSE02THk5c2FETXVaMjl2WjJ4bGRYTmxjbU52Ym5SbGJuUXVZMjl0TDJFdlFVTm5PRzlqU21aRVVHWTNlV2t6Um1KcGVXcExWRUl3VkRWUVpqWkVRM0U1WVdwQ1l6RkVObDlGVFhsUVdHcGlSVmxFV1ZOQk9HNTBaejF6T1RZdFl5SXNJbkJ5YjNacFpHVnlYMmxrSWpvaU1UQTBNVGMzT1RrNU1UQTBNVEV4TVRrM09ESTVJaXdpYzNWaUlqb2lNVEEwTVRjM09UazVNVEEwTVRFeE1UazNPREk1SW4wc0luSnZiR1VpT2lKaGRYUm9aVzUwYVdOaGRHVmtJaXdpWVdGc0lqb2lZV0ZzTVNJc0ltRnRjaUk2VzNzaWJXVjBhRzlrSWpvaWIyRjFkR2dpTENKMGFXMWxjM1JoYlhBaU9qRTNNemt6TURZME1qVjlYU3dpYzJWemMybHZibDlwWkNJNkltSTNNekkyWVRBM0xUSTFNall0TkRSbE1pMDRPVFprTFdVelpHRXhPVFk1WmpNeVpTSXNJbWx6WDJGdWIyNTViVzkxY3lJNlptRnNjMlY5LnJMU3I1YTdXSlJUZFlZVmJqcDMxU3BLWkpqazhBVjBOTldWZnlvWWd1bW8iLCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwiZXhwaXJlc19pbiI6NjA0ODAwLCJleHBpcmVzX2F0IjoxNzM5OTExMjI1LCJyZWZyZXNoX3Rva2VuIjoibW5mSFFHeTNFczBSQnJEdGpSZ0ZCZyIsInVzZXIiOnsiaWQiOiJkZmI4OTIxYi1lZjU0LTQ4M2MtYmZhNC1mZWU2OGYyNWM1NDIiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJlbWFpbCI6Imx1Y2FiZXJ0aW5pbHVjYUBnbWFpbC5jb20iLCJlbWFpbF9jb25maXJtZWRfYXQiOiIyMDI1LTAyLTEwVDIxOjEwOjM1LjI1MDM3WiIsInBob25lIjoiIiwiY29uZmlybWVkX2F0IjoiMjAyNS0wMi0xMFQyMToxMDozNS4yNTAzN1oiLCJsYXN0X3NpZ25faW5fYXQiOiIyMDI1LTAyLTExVDIwOjQwOjI1LjAzNDk2MDM3MVoiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJnb29nbGUiLCJwcm92aWRlcnMiOlsiZ29vZ2xlIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKZkRQZjd5aTNGYml5aktUQjBUNVBmNkRDcTlhakJjMUQ2X0VNeVBYamJFWURZU0E4bnRnPXM5Ni1jIiwiZW1haWwiOiJsdWNhYmVydGluaWx1Y2FAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6Ikx1Y2EgQmVydGluaSIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbSIsIm5hbWUiOiJMdWNhIEJlcnRpbmkiLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKZkRQZjd5aTNGYml5aktUQjBUNVBmNkRDcTlhakJjMUQ2X0VNeVBYamJFWURZU0E4bnRnPXM5Ni1jIiwicHJvdmlkZXJfaWQiOiIxMDQxNzc5OTkxMDQxMTExOTc4MjkiLCJzdWIiOiIxMDQxNzc5OTkxMDQxMTExOTc4MjkifSwiaWRlbnRpdGllcyI6W3siaWRlbnRpdHlfaWQiOiI1MTczYzM1MC1hNDQ0LTQ1ZDItOGZkMy1kM2QwNWM5YzBkODciLCJpZCI6IjEwNDE3Nzk5OTEwNDExMTE5NzgyOSIsInVzZ")  # Sostituisci con il tuo token"
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
# Post-elaborazione del file audio generato
# Carichiamo il file audio, lo adattiamo a 2 minuti e lo salviamo come "song_2min.mp3"
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

# Esporta il file audio finale
output_path = "song_2min.mp3"
song_2min.export(output_path, format="mp3")
print("DEBUG: Canzone finale esportata con successo in:", output_path)
