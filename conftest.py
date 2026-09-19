import pytest
from data import register_new_courier, get_courier_id_by_login, delete_courier


@pytest.fixture
def new_courier_data():
    """Возвращает данные нового курьера (словарь с login, password, firstName)."""
    data = register_new_courier()
    assert data, "Не удалось зарегистрировать нового курьера"
    return data


@pytest.fixture
def created_courier(new_courier_data):
    """
    Создаёт курьера (он уже создан в new_courier_data) и после теста удаляет его.
    Возвращает данные курьера.
    """
    courier_id = get_courier_id_by_login(
        new_courier_data["login"], new_courier_data["password"]
    )
    # Если вдруг не смогли получить ID — не ломаем фикстуру, но предупредим
    yield new_courier_data

    if courier_id is not None:
        delete_courier(courier_id)
