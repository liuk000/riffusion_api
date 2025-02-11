import os
from riffusion_api import RiffusionAPI
from pydub import AudioSegment

# Inserisci qui il token ottenuto seguendo le istruzioni dal sito Riffusion (vedi README del repository )
SB_API_AUTH_TOKEN = "base64-eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0ltdHBaQ0k2SW1aclQzQnNSMnQxWTA4MVkyMUJRaklpTENKMGVYQWlPaUpLVjFRaWZRLmV5SnBjM01pT2lKb2RIUndjem92TDJobmRIQjZkV3RsZW05a2VISm5iV1pvYkhaNUxuTjFjR0ZpWVhObExtTnZMMkYxZEdndmRqRWlMQ0p6ZFdJaU9pSmtabUk0T1RJeFlpMWxaalUwTFRRNE0yTXRZbVpoTkMxbVpXVTJPR1l5TldNMU5ESWlMQ0poZFdRaU9pSmhkWFJvWlc1MGFXTmhkR1ZrSWl3aVpYaHdJam94TnpNNU9URXhNakkxTENKcFlYUWlPakUzTXprek1EWTBNalVzSW1WdFlXbHNJam9pYkhWallXSmxjblJwYm1sc2RXTmhRR2R0WVdsc0xtTnZiU0lzSW5Cb2IyNWxJam9pSWl3aVlYQndYMjFsZEdGa1lYUmhJanA3SW5CeWIzWnBaR1Z5SWpvaVoyOXZaMnhsSWl3aWNISnZkbWxrWlhKeklqcGJJbWR2YjJkc1pTSmRmU3dpZFhObGNsOXRaWFJoWkdGMFlTSTZleUpoZG1GMFlYSmZkWEpzSWpvaWFIUjBjSE02THk5c2FETXVaMjl2WjJ4bGRYTmxjbU52Ym5SbGJuUXVZMjl0TDJFdlFVTm5PRzlqU21aRVVHWTNlV2t6Um1KcGVXcExWRUl3VkRWUVpqWkVRM0U1WVdwQ1l6RkVObDlGVFhsUVdHcGlSVmxFV1ZOQk9HNTBaejF6T1RZdFl5SXNJbVZ0WVdsc0lqb2liSFZqWVdKbGNuUnBibWxzZFdOaFFHZHRZV2xzTG1OdmJTSXNJbVZ0WVdsc1gzWmxjbWxtYVdWa0lqcDBjblZsTENKbWRXeHNYMjVoYldVaU9pSk1kV05oSUVKbGNuUnBibWtpTENKcGMzTWlPaUpvZEhSd2N6b3ZMMkZqWTI5MWJuUnpMbWR2YjJkc1pTNWpiMjBpTENKdVlXMWxJam9pVEhWallTQkNaWEowYVc1cElpd2ljR2h2Ym1WZmRtVnlhV1pwWldRaU9tWmhiSE5sTENKd2FXTjBkWEpsSWpvaWFIUjBjSE02THk5c2FETXVaMjl2WjJ4bGRYTmxjbU52Ym5SbGJuUXVZMjl0TDJFdlFVTm5PRzlqU21aRVVHWTNlV2t6Um1KcGVXcExWRUl3VkRWUVpqWkVRM0U1WVdwQ1l6RkVObDlGVFhsUVdHcGlSVmxFV1ZOQk9HNTBaejF6T1RZdFl5SXNJbkJ5YjNacFpHVnlYMmxrSWpvaU1UQTBNVGMzT1RrNU1UQTBNVEV4TVRrM09ESTVJaXdpYzNWaUlqb2lNVEEwTVRjM09UazVNVEEwTVRFeE1UazNPREk1SW4wc0luSnZiR1VpT2lKaGRYUm9aVzUwYVdOaGRHVmtJaXdpWVdGc0lqb2lZV0ZzTVNJc0ltRnRjaUk2VzNzaWJXVjBhRzlrSWpvaWIyRjFkR2dpTENKMGFXMWxjM1JoYlhBaU9qRTNNemt6TURZME1qVjlYU3dpYzJWemMybHZibDlwWkNJNkltSTNNekkyWVRBM0xUSTFNall0TkRSbE1pMDRPVFprTFdVelpHRXhPVFk1WmpNeVpTSXNJbWx6WDJGdWIyNTViVzkxY3lJNlptRnNjMlY5LnJMU3I1YTdXSlJUZFlZVmJqcDMxU3BLWkpqazhBVjBOTldWZnlvWWd1bW8iLCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwiZXhwaXJlc19pbiI6NjA0ODAwLCJleHBpcmVzX2F0IjoxNzM5OTExMjI1LCJyZWZyZXNoX3Rva2VuIjoibW5mSFFHeTNFczBSQnJEdGpSZ0ZCZyIsInVzZXIiOnsiaWQiOiJkZmI4OTIxYi1lZjU0LTQ4M2MtYmZhNC1mZWU2OGYyNWM1NDIiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJlbWFpbCI6Imx1Y2FiZXJ0aW5pbHVjYUBnbWFpbC5jb20iLCJlbWFpbF9jb25maXJtZWRfYXQiOiIyMDI1LTAyLTEwVDIxOjEwOjM1LjI1MDM3WiIsInBob25lIjoiIiwiY29uZmlybWVkX2F0IjoiMjAyNS0wMi0xMFQyMToxMDozNS4yNTAzN1oiLCJsYXN0X3NpZ25faW5fYXQiOiIyMDI1LTAyLTExVDIwOjQwOjI1LjAzNDk2MDM3MVoiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJnb29nbGUiLCJwcm92aWRlcnMiOlsiZ29vZ2xlIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKZkRQZjd5aTNGYml5aktUQjBUNVBmNkRDcTlhakJjMUQ2X0VNeVBYamJFWURZU0E4bnRnPXM5Ni1jIiwiZW1haWwiOiJsdWNhYmVydGluaWx1Y2FAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6Ikx1Y2EgQmVydGluaSIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbSIsIm5hbWUiOiJMdWNhIEJlcnRpbmkiLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKZkRQZjd5aTNGYml5aktUQjBUNVBmNkRDcTlhakJjMUQ2X0VNeVBYamJFWURZU0E4bnRnPXM5Ni1jIiwicHJvdmlkZXJfaWQiOiIxMDQxNzc5OTkxMDQxMTExOTc4MjkiLCJzdWIiOiIxMDQxNzc5OTkxMDQxMTExOTc4MjkifSwiaWRlbnRpdGllcyI6W3siaWRlbnRpdHlfaWQiOiI1MTczYzM1MC1hNDQ0LTQ1ZDItOGZkMy1kM2QwNWM5YzBkODciLCJpZCI6IjEwNDE3Nzk5OTEwNDExMTE5NzgyOSIsInVzZ"  # Sostituisci con il tuo token





# Inizializza l'API di Riffusion
api = RiffusionAPI(sb_api_auth_tokens_0=SB_API_AUTH_TOKEN)

# Definisci il testo personalizzato per la canzone
custom_text = (
    "Questo è il mio testo personalizzato: la vita è un viaggio, "
    "dove ogni istante è una melodia che ci guida nel tempo. "
    "Cantiamo insieme, in un abbraccio di note e sogni."
        "Questo è il mio testo personalizzato: la vita è un viaggio, "
    "dove ogni istante è una melodia che ci guida nel tempo. "
    "Cantiamo insieme, in un abbraccio di note e sogni."
)

# Costruisci il prompt. Puoi scegliere di includere indicatori come [Vocal] per enfatizzare la presenza di voce.
prompt = f"[Vocal] {custom_text}"

# Specifica lo stile musicale (ad esempio "pop", "rock", "gitar" o altri stili supportati)
music_style = "avant-garde 70s music"

# Genera la traccia. Il parametro output_file indica il nome del file generato.
track = api.generate(prompt=prompt, music_style=music_style, output_file="song.mp3")

# Mostra il testo generato (eventualmente dalla risposta della API)
print("Testo generato:")
print(track.lyrics)
print("File generato:", track.result_file_path)

# Carica il file audio generato utilizzando pydub
song = AudioSegment.from_file(track.result_file_path, format="mp3")

# Definisci la durata target: 2 minuti (120000 millisecondi)
target_duration_ms = 2 * 60 * 1000  # 120000 ms

# Se la traccia è più lunga di 2 minuti, la tagliamo; se è più corta, aggiungiamo silenzio alla fine.
if len(song) > target_duration_ms:
    song_2min = song[:target_duration_ms]
    print("La traccia è stata tagliata a 2 minuti.")
elif len(song) < target_duration_ms:
    silence_duration = target_duration_ms - len(song)
    silence = AudioSegment.silent(duration=silence_duration)
    song_2min = song + silence
    print("È stato aggiunto silenzio per raggiungere i 2 minuti.")
else:
    song_2min = song
    print("La traccia è già esattamente di 2 minuti.")

# Esporta il file audio finale
output_path = "song_2min.mp3"
song_2min.export(output_path, format="mp3")
print("Canzone finale salvata in:", output_path)
