import pytest
import requests
from helpers import generate_random_string
from data import LOGIN_COURIER_URL  # <-- добавлен импорт
import allure


@allure.feature("Авторизация курьера")
@allure.story("Вход в систему")
class TestCourierLogin:

    @allure.step("Выполнить логин курьера")
    def _login_courier(self, login, password):
        payload = {"login": login, "password": password}
        return requests.post(LOGIN_COURIER_URL, json=payload)

    @allure.title("Позитивный сценарий: успешный логин возвращает id курьера (200)")
    def test_successful_login_returns_id(self, created_courier):
        response = self._login_courier(
            created_courier["login"], created_courier["password"]
        )

        assert response.status_code == 200, f"Ожидался 200 при логине, получено {response.status_code}"
        assert "id" in response.json(), "В ответе нет поля 'id'"
        assert isinstance(response.json()["id"], int), "'id' должен быть числом"

    @allure.title("Негативный сценарий: запрос без логина возвращает ошибку 400")
    def test_login_without_login_field_returns_error(self):
        payload = {"password": generate_random_string(10)}

        with allure.step("Отправить POST-запрос на логин без поля login"):
            response = requests.post(LOGIN_COURIER_URL, json=payload)

        assert response.status_code == 400, f"Ожидался 400 при отсутствии login, получено {response.status_code}"
        assert response.json().get("message") == "Недостаточно данных для входа", "Сообщение об ошибке не совпадает с документацией"

    @allure.title("Негативный сценарий: запрос без пароля возвращает ошибку 400")
    def test_login_without_password_field_returns_error(self):
        payload = {"login": generate_random_string(10)}

        with allure.step("Отправить POST-запрос на логин без поля password"):
            response = requests.post(LOGIN_COURIER_URL, json=payload)

        assert response.status_code == 400, f"Ожидался 400 при отсутствии password, получено {response.status_code}"
        assert response.json().get("message") == "Недостаточно данных для входа", "Сообщение не совпадает с документацией"

    @allure.title("Негативный сценарий: неверный пароль возвращает ошибку 404")
    def test_login_with_wrong_password_returns_not_found(self, created_courier):
        with allure.step("Попытаться залогиниться с неверным паролем"):
            payload_login = {"login": created_courier["login"], "password": "wrong_password"}
            response = requests.post(LOGIN_COURIER_URL, json=payload_login)

        assert response.status_code == 404, f"Ожидался 404 при неверном пароле, получено {response.status_code}"
        assert response.json().get("message") == "Учетная запись не найдена", "Сообщение не совпадает с документацией"

    @allure.title("Негативный сценарий: логин несуществующего пользователя возвращает ошибку 404")
    def test_login_with_nonexistent_user_returns_not_found(self):
        nonexistent_login = "nonexistent_" + generate_random_string(5)
        password = generate_random_string(10)

        with allure.step("Попытаться залогиниться под несуществующим логином"):
            payload = {"login": nonexistent_login, "password": password}
            response = requests.post(LOGIN_COURIER_URL, json=payload)

        assert response.status_code == 404, f"Ожидался 404 для несуществующего пользователя, получено {response.status_code}"
        assert response.json().get("message") == "Учетная запись не найдена", "Сообщение не совпадает с документацией"

    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_login_missing_required_field_returns_400(self, missing_field):
        allure.dynamic.title(f"Негативный сценарий: отсутствует поле '{missing_field}' — ожидается ошибка 400")

        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
        }
        del payload[missing_field]

        with allure.step(f"Отправить POST-запрос без обязательного поля '{missing_field}'"):
            response = requests.post(LOGIN_COURIER_URL, json=payload)

        assert response.status_code == 400, f"Ожидался 400 при отсутствии '{missing_field}', получено {response.status_code}"
        assert response.json().get("message") == "Недостаточно данных для входа", "Сообщение не совпадает с документацией"
