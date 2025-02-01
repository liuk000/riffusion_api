<p align="center">
  <img src="https://raw.githubusercontent.com/Badim41/riffusion_api/Logo.png" width="300px" height="300px"/>
</p>

<h1 align="center">Ruffusion API</h1>

<div align="center">

[![Riffusion](https://img.shields.io/badge/Riffusion-Visit-blue?style=flat&logo=googlechrome)](https://www.riffusion.com)
[![Example Usage Bot](https://img.shields.io/badge/Example-Telegram--BOT-0066FF?logo=probot&style=flat)](https://t.me/riffusion_unlimit_bot)

</div>

---

## 📚 О библиотеке

**Ruffusion API Library** — это неофициальный Python-клиент для взаимодействия с генератором музыки **[Riffusion](https://www.riffusion.com)**.  
Библиотека упрощает создание музыки с помощью модели **FUZZ-0.7** и включает основные функции сервиса.

---

## 🚀 Установка

Установите библиотеку через `pip`:

```sh
pip install git+https://github.com/Badim41/riffusion_api.git
```

---

## 🔑 Получение `sb_api_auth_tokens_0`

Чтобы использовать API, необходимо получить токен `sb_api_auth_tokens_0`.

1. Откройте сайт [Riffusion](https://www.riffusion.com).
2. Перейдите в **DevTools** (`F12` или `Ctrl+Shift+I`).
3. Откройте вкладку **Application** → **Cookies**.
4. Найдите `sb-api-auth-token.0` и скопируйте его значение
5. Передайте токен (или список токенов) в класс **RiffusionAPI**.
<p align="center">
  <img src="https://raw.githubusercontent.com/Badim41/riffusion_api/screenshoot.png" width="500px" height="300px"/>
</p>

---

### 📌 Пример генерации
```python
from riffusion_api import RiffusionAPI

account = RiffusionAPI(sb_api_auth_tokens_0="base64-eyJ...")  # provide list or str account token
track = account.generate(prompt="[Instrumental]", music_style="gitar")

print(track.lyrics)
print(track.result_file_path)
```

---

### ↔ Extend (Расширение)
```python
from riffusion_api import RiffusionAPI, RiffusionTransformType

account = RiffusionAPI(sb_api_auth_tokens_0="base64-eyJ...")  # provide list or str account token
track = account.generate(output_file="extend.mp3",
                         prompt="[Instrumental]",
                         music_style="gitar",
                         transform=RiffusionTransformType.extend,
                         input_file="file.mp3")

print(track.lyrics)
print(track.result_file_path)
```

---

### 🎤 Cover (Кавер)
```python
from riffusion_api import RiffusionAPI, RiffusionTransformType

account = RiffusionAPI(sb_api_auth_tokens_0="base64-eyJ...")  # provide list or str account token
track = account.generate(output_file="caver.mp3",
                         prompt="[Instrumental]",
                         music_style="gitar",
                         transform=RiffusionTransformType.cover,
                         input_file="file.mp3")

print(track.lyrics)
print(track.result_file_path)
```

---