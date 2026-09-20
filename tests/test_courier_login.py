import pytest
import requests
from data import LOGIN_COURIER_URL, CREATE_COURIER_URL, generate_random_string, get_courier_id_by_login, delete_courier
import allure

@allure.feature("Авторизация курьера")
@allure.story("Вход в систему")
class TestCourierLogin:

    @staticmethod
    @allure.step("Удалить тестового курьера")
    
    def _cleanup_safe(login, password):
        try:
            courier_id = get_courier_id_by_login(login, password)
            delete_courier(courier_id)
        except Exception:
            pass

    @allure.step("Создать курьера через эндпоинт создания")
    def _create_courier(self, login, password, first_name):
        payload = {
            "login": login,
            "password": password,
            "firstName": first_name,
        }
        return requests.post(CREATE_COURIER_URL, json=payload)

    @allure.step("Выполнить логин курьера")
    def _login_courier(self, login, password):
        payload = {"login": login, "password": password}
        return requests.post(LOGIN_COURIER_URL, json=payload)

    @allure.title("Позитивный сценарий: успешный логин возвращает id курьера (200)")
    def test_successful_login_returns_id(self):
        login = generate_random_string(10)
        password = generate_random_string(10)
        first_name = generate_random_string(10)

        response_create = self._create_courier(login, password, first_name)
        assert response_create.status_code == 201, f"Ожидался 201 при создании курьера, получено {response_create.status_code}. URL: {CREATE_COURIER_URL}"

        response = self._login_courier(login, password)

        assert response.status_code == 200, f"Ожидался 200 при логине, получено {response.status_code}"
        assert "id" in response.json(), "В ответе нет поля 'id'"
        assert isinstance(response.json()["id"], int), "'id' должен быть числом"

        self._cleanup_safe(login, password)

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
        assert response.json().get("message") == "Недостаточно данных для входа", "Сообщение об ошибке не совпадает с документацией"

    @allure.title("Негативный сценарий: неверный пароль возвращает ошибку 404")
    def test_login_with_wrong_password_returns_not_found(self):
        login = generate_random_string(10)
        password = generate_random_string(10)
        wrong_password = "wrong_password"
        first_name = generate_random_string(10)

        response_create = self._create_courier(login, password, first_name)
        assert response_create.status_code == 201, f"Ожидался 201 при создании курьера, получено {response_create.status_code}"

        with allure.step("Попытаться залогиниться с неверным паролем"):
            payload_login = {"login": login, "password": wrong_password}
            response = requests.post(LOGIN_COURIER_URL, json=payload_login)

        assert response.status_code == 404, f"Ожидался 404 при неверном пароле, получено {response.status_code}"
        assert response.json().get("message") == "Учетная запись не найдена", "Сообщение не совпадает с документацией"

        self._cleanup_safe(login, password)

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
