import pytest
import requests
from data import BASE_URL, generate_random_string
import allure


@allure.feature("Управление заказами")
@allure.story("Создание заказа")
class TestOrderCreation:

    @staticmethod
    def _generate_order_payload(color=None):
        """Генерирует payload для создания заказа"""
        payload = {
            "firstName": "Naruto",
            "lastName": "Uchiha",
            "address": "Konoha, 142 apt.",
            "metroStation": 4,
            "phone": "+7 800 355 35 35",
            "rentTime": 5,
            "deliveryDate": "2020-06-06",
            "comment": "Saske, come back to Konoha",
        }
        if color is not None:
            payload["color"] = color
        return payload

    @staticmethod
    def _cancel_order_safe(track):
        """Безопасная отмена заказа, чтобы не засорять базу"""
        try:
            requests.put(f"{BASE_URL}/api/v1/orders/cancel", json={"track": track})
        except Exception:
            pass

    @pytest.mark.parametrize(
        "color,description",
        [
            (["BLACK"], "указан только цвет BLACK"),
            (["GREY"], "указан только цвет GREY"),
            (["BLACK", "GREY"], "указаны оба цвета BLACK и GREY"),
            (None, "цвет не указан вообще"),
        ],
    )
    @allure.title("Создание заказа: {description}")
    def test_create_order_with_color_variants(self, color, description):
        payload = self._generate_order_payload(color)
        response = requests.post(f"{BASE_URL}/api/v1/orders", json=payload)

        assert response.status_code == 201, (
            f"Ожидался 201, получено {response.status_code}. Тело: {response.text}"
        )
        assert "track" in response.json(), "В ответе отсутствует поле 'track'"
        assert isinstance(response.json()["track"], int), "track должен быть числом"

        # Очищаем созданный заказ
        self._cancel_order_safe(response.json()["track"])
