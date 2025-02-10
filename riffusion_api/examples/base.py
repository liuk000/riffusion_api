from riffusion_api import RiffusionAPI

account = RiffusionAPI(sb_api_auth_tokens_0=[]) # provide list or str account token
track = account.generate(prompt="[Instrumental]", music_style="gitar", input_file=r"E:\Games\for suno\i want minus.mp3")

print(track.lyrics)
print(track.result_file_path)