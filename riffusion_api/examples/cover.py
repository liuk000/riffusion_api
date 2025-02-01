from riffusion_api import RiffusionAPI, RiffusionTransformType

account = RiffusionAPI(sb_api_auth_tokens_0="base64-eyJ...") # provide list or str account token
track = account.generate(prompt="[Instrumental]",
                         music_style="gitar",
                         transform=RiffusionTransformType.cover,
                         input_file="file.mp3")

print(track.lyrics)
print(track.result_file_path)