import pytest

from backend.container import reset_container


@pytest.fixture(autouse=True)
def isolated_container():
    reset_container()
    yield
    reset_container()
