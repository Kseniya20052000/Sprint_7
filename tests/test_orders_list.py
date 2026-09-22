import pytest
import requests
import json
from helpers import generate_random_string
from data import BASE_URL
from api_client import delete_courier
import allure


@allure.feature("Управление заказами")
@allure.story("Получение списка заказов")
class TestOrdersList:

    @staticmethod
    @allure.step("Создать курьера для теста")
    def _create_courier():
        """Создаёт курьера и возвращает его id."""
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        resp = requests.post(f"{BASE_URL}/api/v1/courier", json=payload)
        assert resp.status_code == 201, f"Не удалось создать курьера: {resp.status_code}"
        return resp.json()["id"]

    @allure.step("Получить список заказов по URL {url}")
    def _get_orders(self, url):
        return requests.get(url)

    @allure.title("Базовый сценарий: получение списка заказов без фильтров")
    def test_get_orders_without_filters(self):
        url = f"{BASE_URL}/api/v1/orders"

        with allure.step("Запросить список заказов без фильтров"):
            response = self._get_orders(url)

        assert response.status_code == 200, f"Ожидался 200, получено {response.status_code}"
        data = response.json()
        assert "orders" in data and isinstance(data["orders"], list)
        assert "pageInfo" in data
        assert "availableStations" in data

    @allure.title("Фильтрация по courierId: заказы существующего курьера (создан в тесте)")
    def test_get_orders_by_existing_courier_id(self):
        courier_id = self._create_courier()

        url = f"{BASE_URL}/api/v1/orders?courierId={courier_id}"

        with allure.step(f"Запросить список заказов для courierId={courier_id}"):
            response = self._get_orders(url)

        assert response.status_code == 200, f"Ожидался 200 для курьера {courier_id}, получено {response.status_code}"
        data = response.json()
        assert "orders" in data and isinstance(data["orders"], list)

        for order in data["orders"]:
            assert order.get("courierId") == courier_id or order.get("courierId") is None, (
                f"В списке заказов курьера {courier_id} найден заказ с другим courierId"
            )

        delete_courier(courier_id)

    @allure.title("Фильтрация по courierId: несуществующий курьер — ожидается 404")
    def test_get_orders_by_nonexistent_courier_id(self):
        courier_id = 999999
        url = f"{BASE_URL}/api/v1/orders?courierId={courier_id}"

        with allure.step(f"Запросить список заказов для несуществующего courierId={courier_id}"):
            response = self._get_orders(url)

        assert response.status_code == 404, f"Для несуществующего courierId ожидался 404, получено {response.status_code}"
        assert "message" in response.json(), "При 404 должно быть поле message"

    @pytest.mark.parametrize(
        "stations,description",
        [
            (["1", "2"], "фильтр по станциям 1 и 2"),
            (["999"], "несуществующая станция — список может быть пустым, но статус 200"),
        ],
    )
    @allure.title("Фильтрация по nearestStation: {description}")
    def test_get_orders_by_nearest_station(self, stations, description):
        payload_json = json.dumps(stations)
        url = f"{BASE_URL}/api/v1/orders?nearestStation={payload_json}"

        with allure.step(f"Запросить заказы с фильтром nearestStation={stations}"):
            response = self._get_orders(url)

        assert response.status_code == 200, f"Ожидался 200 при фильтрации по станциям, получено {response.status_code}"

        data = response.json()
        assert "orders" in data and isinstance(data["orders"], list)

        for order in data["orders"]:
            assert order.get("metroStation") in stations, (
                f"Заказ с metroStation={order.get('metroStation')} не соответствует фильтру {stations}"
            )

    @allure.title("Пагинация: limit и page")
    def test_pagination_limit_and_page(self):
        limit = 5
        page = 0
        url = f"{BASE_URL}/api/v1/orders?limit={limit}&page={page}"

        with allure.step(f"Запросить заказы с пагинацией: limit={limit}, page={page}"):
            response = self._get_orders(url)

        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "pageInfo" in data

        page_info = data["pageInfo"]
        assert page_info.get("limit") == limit
        assert page_info.get("page") == page
        assert len(data["orders"]) <= limit
        assert page_info.get("total") is not None
        assert page_info["total"] >= len(data["orders"])
