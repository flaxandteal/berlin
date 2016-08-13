import pytest
from berlin import state
from berlin import subdivision

@pytest.fixture
def subdiv_dict(state_dict):
    subdiv_dict = {
        'BE:VAN': {
            'name': 'Antwerpen (VLG)',
            'supercode': 'BE',
            'subcode': 'VAN',
            'level': 'Province',
            'state': 'BE'
        },
        'BE:WNA': {
            'name': 'Namur (WLA)',
            'supercode': 'BE',
            'subcode': 'WNA',
            'level': 'Province',
            'state': 'BE'
        }
    }

    return subdiv_dict

@pytest.fixture
def state_dict():
    state_dict = {
        'BE': {
            'name': 'Belgium',
            'alpha2': 'BE'
        },
        'DE': {
            'name': 'Germany',
            'alpha2': 'DE',
        }
    }

    return {k: state.State(k, **v) for k, v in state_dict.items()}


class TestSubdivision:
    def test_can_create_simple_subdivision(self, subdiv_dict, state_dict):
        key, item = list(subdiv_dict.items())[0]

        state_service = lambda st: state_dict[st]
        lcde = subdivision.SubDivision(state_service, key, **item)

        assert str(lcde) == key
        assert dict(lcde) == item
