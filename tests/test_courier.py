import pytest
import requests
from data import CREATE_COURIER_URL, generate_random_string, get_courier_id_by_login, delete_courier
import allure


@allure.feature("Управление курьерами")
@allure.story("Создание курьера")
class TestCourierCreation:

    @allure.step("Создать курьера POST-запросом")
    def _create_courier(self, payload):
        return requests.post(CREATE_COURIER_URL, json=payload)

    @staticmethod
    def _cleanup(login, password):
        courier_id = get_courier_id_by_login(login, password)
        delete_courier(courier_id)

    @allure.title("Позитивный сценарий: создание курьера возвращает статус 201")
    def test_create_courier_success(self):
        """Курьера можно создать; запрос возвращает правильный код ответа (201)."""
        login = generate_random_string(10)
        password = generate_random_string(10)
        firstName = generate_random_string(10)

        payload = {"login": login, "password": password, "firstName": firstName}

        try:
            with allure.step("Отправить запрос на создание курьера"):
                response = self._create_courier(payload)
            assert response.status_code == 201
        finally:
            self._cleanup(login, password)

    @allure.title("Позитивный сценарий: успешный запрос возвращает ok=true")
    def test_create_courier_returns_ok_true(self):
        """Успешный запрос возвращает {"ok": true}."""
        login = generate_random_string(10)
        password = generate_random_string(10)
        firstName = generate_random_string(10)

        payload = {"login": login, "password": password, "firstName": firstName}

        try:
            with allure.step("Отправить запрос на создание курьера и проверить ответ"):
                response = self._create_courier(payload)
                assert response.status_code == 201
                assert response.json() == {"ok": True}
        finally:
            self._cleanup(login, password)

    @allure.title("Негативный сценарий: нельзя создать двух курьеров с одинаковыми данными")
    def test_create_two_identical_couriers_fails(self, created_courier):
        """Нельзя создать двух одинаковых курьеров."""
        # created_courier уже создан фикстурой — пытаемся создать такого же
        with allure.step("Второй запрос: повторно создать курьера с теми же данными (ожидается 409)"):
            response = self._create_courier(created_courier)
            assert response.status_code == 409, f"Ожидался 409 при дубликате логина, получено {response.status_code}"

    @allure.title("Негативный сценарий: попытка создания курьера с существующим логином возвращает ошибку")
    def test_create_courier_duplicate_login_returns_error(self, created_courier):
        """Если создать пользователя с логином, который уже есть — возвращается ошибка."""
        payload2 = {
            "login": created_courier["login"],
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        with allure.step("Попытаться создать второго курьера с тем же логином (ожидается 409)"):
            response = self._create_courier(payload2)
            assert response.status_code == 409, f"Ожидался 409 при повторном логине, получено {response.status_code}"

    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_create_courier_missing_field_returns_error(self, missing_field):
        """Если одного из полей нет, запрос возвращает ошибку 400."""
        allure.dynamic.title(f"Негативный сценарий: отсутствует поле '{missing_field}' — ожидается ошибка 400")

        login = generate_random_string(10)
        password = generate_random_string(10)
        firstName = generate_random_string(10)

        payload = {"login": login, "password": password, "firstName": firstName}
        del payload[missing_field]

        with allure.step(f"Отправить запрос без поля '{missing_field}' (ожидается 400)"):
            response = self._create_courier(payload)
            assert response.status_code == 400, f"Ожидался 400 при отсутствии '{missing_field}', получено {response.status_code}"
            assert "message" in response.json(), "При ошибке должен быть ключ 'message' в ответе"
