import pytest
from berlin import state

@pytest.fixture()
def state_dict():
    return {
        'DE': {
            'name': 'Germany',
            'alpha2': 'DE'
        }
    }


class TestState:
    def test_can_create_simple_state(self, state_dict):
        key, item = list(state_dict.items())[0]

        lcde = state.State(key, **item)

        assert str(lcde) == key
        assert dict(lcde) == item
