import pytest
import requests
from data import CREATE_COURIER_URL, generate_random_string, get_courier_id_by_login, delete_courier
import allure

@allure.feature("Управление курьерами")
@allure.story("Создание курьера")
class TestCourierCreation:

    @allure.title("Позитивный сценарий: создание курьера возвращает статус 201")
    def test_create_courier_success(self):
        """курьера можно создать; запрос возвращает правильный код ответа (201)."""
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        
        response = requests.post(CREATE_COURIER_URL, json=payload) 
        assert response.status_code == 201
        self._cleanup(payload["login"], payload["password"])

    @allure.title("Позитивный сценарий: успешный запрос возвращает {{\"ok\": true}}")
    def test_create_courier_returns_ok_true(self):
        """успешный запрос возвращает {"ok": true}."""
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        
        response = requests.post(CREATE_COURIER_URL, json=payload)
        assert response.status_code == 201
        assert response.json() == {"ok": True}
        self._cleanup(payload["login"], payload["password"])

    @allure.title("Негативный сценарий: нельзя создать двух курьеров с одинаковыми данными")
    def test_create_two_identical_couriers_fails(self):
        """нельзя создать двух одинаковых курьеров."""
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        response1 = requests.post(CREATE_COURIER_URL, json=payload)
        assert response1.status_code == 201

        response2 = requests.post(CREATE_COURIER_URL, json=payload)
        assert response2.status_code == 409
        assert "Этот логин уже используется" in response2.json()["message"]
        self._cleanup(payload["login"], payload["password"])

    @allure.title("Негативный сценарий: попытка создания курьера с существующим логином возвращает ошибку")
    def test_create_courier_duplicate_login_returns_error(self):
        """если создать пользователя с логином, который уже есть — возвращается ошибка."""
        payload1 = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        response1 = requests.post(CREATE_COURIER_URL, json=payload1)
        assert response1.status_code == 201

        payload2 = {
            "login": payload1["login"],
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        response2 = requests.post(CREATE_COURIER_URL, json=payload2)
        assert response2.status_code == 409
        assert "Этот логин уже используется" in response2.json()["message"]
        self._cleanup(payload1["login"], payload1["password"])

    @pytest.mark.parametrize("missing_field", ["login", "password", "firstName"])
    def test_create_courier_missing_field_returns_error(self, missing_field):
        """если одного из полей нет, запрос возвращает ошибку 400."""
        allure.dynamic.title(f"Негативный сценарий: отсутствует поле '{missing_field}' — ожидается ошибка 400")
        
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        del payload[missing_field]

        
        response = requests.post(CREATE_COURIER_URL, json=payload)
        
        
        
        assert response.status_code == 400
        assert response.json()["message"] == "Недостаточно данных для создания учетной записи"

    @staticmethod
    def _cleanup(login, password):
        courier_id = get_courier_id_by_login(login, password)
        if courier_id is not None:
            delete_courier(courier_id)
