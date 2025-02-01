import base64
import hashlib
import json
import random
import string


def decode_and_parse_invalid_base64(encoded_str):
    # Переменная для хранения байтов
    decoded_bytes = bytearray()

    # Проходим по строке по одному символу
    for i in range(0, len(encoded_str), 4):  # шаг по 4 символа
        part = encoded_str[i:i + 4]

        try:
            # Пробуем декодировать текущую часть строки
            decoded_part = base64.b64decode(part + '=' * (-len(part) % 4))
            decoded_bytes.extend(decoded_part)
        except Exception as e:
            # Если возникает ошибка, просто пропускаем эту часть
            continue

    # Преобразуем байты в строку
    decoded_str = decoded_bytes.decode('utf-8', errors='ignore')

    # Исключаем все лишние данные после "full_name"
    decoded_str = decoded_str[:decoded_str.find("full_name") - 2] + "}}}"

    # Парсим строку как JSON
    parsed_data = json.loads(decoded_str)
    return parsed_data


def decode_jwt(token) -> dict:
    try:
        # Разделяем токен на части (Header, Payload, Signature)
        header, payload, signature = token.split('.')

        # Расшифровываем части Header и Payload
        decoded_header = base64.urlsafe_b64decode(header + "==").decode('utf-8')
        decoded_payload = base64.urlsafe_b64decode(payload + "==").decode('utf-8')

        # Парсим JSON-строки в словари
        header_dict = json.loads(decoded_header)
        payload_dict = json.loads(decoded_payload)

        return {
            "header": header_dict,
            "payload": payload_dict
        }
    except Exception as e:
        return {"error": f"Ошибка при расшифровке токена: {e}"}

def random_string(length=8, seed=None, input_str=None):
    if not input_str is None:
        # Создаем хэш входной строки
        hash_object = hashlib.sha256(input_str.encode())
        hash_hex = hash_object.hexdigest()
        # Инициализируем генератор случайных чисел на основе хэша
        random.seed(hash_hex)
    elif not seed is None:
        random.seed(seed)
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))