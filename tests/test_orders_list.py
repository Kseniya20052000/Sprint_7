import pytest
import requests
from data import BASE_URL, generate_random_string
import allure


@allure.feature("Управление заказами")
@allure.story("Получение списка заказов")
class TestOrdersList:

    @staticmethod
    def _create_courier():
        """Создаёт курьера и возвращает его id. Если не получилось — None."""
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10),
        }
        resp = requests.post(f"{BASE_URL}/api/v1/courier/create", json=payload)
        if resp.status_code != 201:
            return None
        return resp.json().get("id")

    @staticmethod
    def _delete_courier(courier_id):
        """Безопасно удаляет курьера (если эндпоинт удаления есть)."""
        try:
            requests.delete(f"{BASE_URL}/api/v1/courier/{courier_id}")
        except Exception:
            pass

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

    @pytest.mark.parametrize(
        "use_existing,description",
        [
            (True, "заказы существующего курьера (создан в тесте)"),
            (False, "несуществующий курьер — ожидается 404"),
        ],
    )
    @allure.title("Фильтрация по courierId: {description}")
    def test_get_orders_by_courier_id(self, use_existing, description):
        courier_id = None
        created_in_test = False

        if use_existing:
            courier_id = self._create_courier()
            if courier_id is None:
                pytest.skip("Не удалось создать курьера для теста (эндпоинт create недоступен или нестабилен)")
            created_in_test = True
        else:
            courier_id = 999999  # заведомо несуществующий

        url = f"{BASE_URL}/api/v1/orders?courierId={courier_id}"

        with allure.step(f"Запросить список заказов для courierId={courier_id}"):
            response = self._get_orders(url)

        if not use_existing:
            # Несуществующий курьер — бэкенд должен вернуть 404
            assert response.status_code == 404, f"Для несуществующего courierId ожидался 404, получено {response.status_code}"
            assert "message" in response.json(), "При 404 должно быть поле message"
            return

        # Для существующего курьера — 200 и список заказов
        assert response.status_code == 200, f"Ожидался 200 для курьера {courier_id}, получено {response.status_code}"
        data = response.json()
        assert "orders" in data and isinstance(data["orders"], list)

        for order in data["orders"]:
            # courierId может быть null, если заказ ещё не назначен — это ок
            assert order.get("courierId") == courier_id or order.get("courierId") is None, (
                f"В списке заказов курьера {courier_id} найден заказ с другим courierId"
            )

        # Очистка: удаляем курьера, которого создали в этом тесте
        if created_in_test:
            self._delete_courier(courier_id)

    @pytest.mark.parametrize(
        "stations,description",
        [
            (["1", "2"], "фильтр по станциям 1 и 2"),
            (["999"], "несуществующая станция — список может быть пустым, но статус 200"),
        ],
    )
    @allure.title("Фильтрация по nearestStation: {description}")
    def test_get_orders_by_nearest_station(self, stations, description):
        import json
        payload_json = json.dumps(stations)
        url = f"{BASE_URL}/api/v1/orders?nearestStation={payload_json}"

        with allure.step(f"Запросить заказы с фильтром nearestStation={stations}"):
            response = self._get_orders(url)

        assert response.status_code == 200, f"Ожидался 200 при фильтрации по станциям, получено {response.status_code}"

        data = response.json()
        assert "orders" in data and isinstance(data["orders"], list)

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
