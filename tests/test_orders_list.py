import pytest
import requests
from data import BASE_URL
import allure

@allure.feature("Управление заказами")
@allure.story("Получение списка заказов")
class TestOrdersList:

    @allure.title("Базовый сценарий: получение списка заказов без фильтров (200 + orders array)")
    def test_get_orders_without_filters(self):
        url = f"{BASE_URL}/api/v1/orders"
        response = requests.get(url)

        assert response.status_code == 200, f"Ожидался 200, получено {response.status_code}"
        assert "orders" in response.json(), "В ответе отсутствует поле 'orders'"
        assert isinstance(response.json()["orders"], list), "'orders' должен быть массивом"
        # Можно проверить, что массив существует, даже если пустой
        assert len(response.json()["orders"]) >= 0, "Длина orders должна быть >= 0"

        # Проверим наличие pageInfo и availableStations — они есть по документации
        assert "pageInfo" in response.json()
        assert "availableStations" in response.json()

    @pytest.mark.parametrize(
        "courier_id,description",
        [
            (1, "заказы курьера с id=1"),
            (999999, "несуществующий курьер — ожидается 404"),
        ],
    )
    @allure.title("Фильтрация по courierId: {description}")
    def test_get_orders_by_courier_id(self, courier_id, description):
        url = f"{BASE_URL}/api/v1/orders?courierId={courier_id}"
        response = requests.get(url)

        if courier_id == 999999:
            # Несуществующий курьер — бэкенд должен вернуть 404
            assert response.status_code == 404, f"Для несуществующего courierId ожидался 404, получено {response.status_code}"
            assert "message" in response.json(), "При 404 должно быть поле message"
            return

        # Для существующего курьера — 200 и список заказов
        assert response.status_code == 200
        assert "orders" in response.json() and isinstance(response.json()["orders"], list)
        # Если заказы есть — каждый должен иметь courierId, равный переданному
        for order in response.json()["orders"]:
            assert order.get("courierId") == courier_id or order.get("courierId") is None, (
                f"В списке заказов курьера {courier_id} найден заказ с другим courierId"
            )

    @pytest.mark.parametrize(
        "stations,description",
        [
            (["1", "2"], "фильтр по станциям 1 и 2"),
            (["999"], "несуществующая станция — список может быть пустым, но статус 200"),
        ],
    )
    @allure.title("Фильтрация по nearestStation: {description}")
    def test_get_orders_by_nearest_station(self, stations, description):
        # nearestStation передаётся как JSON-строка в query-параметре
        import json
        payload_json = json.dumps(stations)
        url = f"{BASE_URL}/api/v1/orders?nearestStation={payload_json}"

        response = requests.get(url)
        assert response.status_code == 200, f"Ожидался 200 при фильтрации по станциям, получено {response.status_code}"

        data = response.json()
        assert "orders" in data and isinstance(data["orders"], list)

        # Проверяем, что все возвращённые заказы имеют metroStation, входящий в фильтр
        # (если список не пустой)
        if len(data["orders"]) > 0:
            for order in data["orders"]:
                assert order.get("metroStation") in stations, (
                    f"Заказ с metroStation={order.get('metroStation')} не соответствует фильтру {stations}"
                )

    @allure.title("Пагинация: limit и page")
    def test_pagination_limit_and_page(self):
        limit = 5
        page = 0
        url = f"{BASE_URL}/api/v1/orders?limit={limit}&page={page}"
        response = requests.get(url)

        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        assert "pageInfo" in data

        page_info = data["pageInfo"]
        assert page_info.get("limit") == limit
        assert page_info.get("page") == page

        # Количество элементов в списке не должно превышать limit
        assert len(data["orders"]) <= limit

        # Дополнительно: total — общее количество заказов — должно быть >= длины списка
        assert page_info.get("total") is not None
        assert page_info["total"] >= len(data["orders"])
