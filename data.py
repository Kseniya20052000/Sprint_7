# data.py
BASE_URL = "https://qa-scooter.praktikum-services.ru"

CREATE_COURIER_URL = f"{BASE_URL}/api/v1/courier"
LOGIN_COURIER_URL = f"{BASE_URL}/api/v1/courier/login"
DELETE_COURIER_URL_TEMPLATE = f"{BASE_URL}/api/v1/courier/{{courier_id}}"
