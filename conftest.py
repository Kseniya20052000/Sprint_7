import pytest
from api_client import register_new_courier, get_courier_id_by_login, delete_courier

@pytest.fixture
def new_courier_data():
    data = register_new_courier()
    assert data, "Не удалось зарегистрировать нового курьера"
    return data

@pytest.fixture
def created_courier(new_courier_data):
    courier_id = get_courier_id_by_login(
        new_courier_data["login"], new_courier_data["password"]
    )
    yield new_courier_data
    delete_courier(courier_id)
