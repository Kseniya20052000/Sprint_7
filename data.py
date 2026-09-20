import requests
import random
import string

BASE_URL = "https://qa-scooter.praktikum-services.ru"

CREATE_COURIER_URL = f"{BASE_URL}/api/v1/courier"
LOGIN_COURIER_URL = f"{BASE_URL}/api/v1/courier/login"
DELETE_COURIER_URL_TEMPLATE = f"{BASE_URL}/api/v1/courier/{{courier_id}}"


def generate_random_string(length=10):
    """Генерирует случайную строку из букв нижнего регистра."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def register_new_courier():
    """
    Регистрирует нового курьера и возвращает словарь с данными.
    Если регистрация не удалась, возвращает пустой словарь.
    """
    login = generate_random_string(10)
    password = generate_random_string(10)
    first_name = generate_random_string(10)

    payload = {
        "login": login,
        "password": password,
        "firstName": first_name,
    }

    response = requests.post(CREATE_COURIER_URL, data=payload)
    if response.status_code == 201:
        return payload
    return {}


def get_courier_id_by_login(login, password):
    """Логинится и возвращает ID курьера. Если не получилось — None."""
    payload = {"login": login, "password": password}
    response = requests.post(LOGIN_COURIER_URL, data=payload)
    if response.status_code == 200:
        return response.json().get("id")
    return None



def delete_courier(courier_id):
    """Удаляет курьера по ID. Возвращает response или None, если ID не передан."""
    if courier_id is None:
        return None
    url = DELETE_COURIER_URL_TEMPLATE.format(courier_id=courier_id)
    return requests.delete(url)
