import pytest
from berlin import locode
from berlin import state
from berlin import subdivision

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

@pytest.fixture()
def locode_dict():
    return {
        'DE:BER': {
            'name': 'Berlin',
            'supercode': 'DE',
            'subcode': 'BER',
            'subdivision_code': 'BE',
            'state': 'DE',
            'function_code': '12345---'
        }
    }

@pytest.fixture()
def subdiv_dict(state_dict):
    subdiv_dict = {
        'DE:BE': {
            'name': 'Berlin',
            'supercode': 'DE',
            'subcode': 'BE',
            'level': 'Länder',
            'state': 'DE'
        }
    }

    state_service = lambda st: state_dict[st]
    subdiv_dict = {c: subdivision.SubDivision(state_service, c, **v) for c, v in subdiv_dict.items()}

    return subdiv_dict



class TestLocode:
    def test_can_create_simple_locode(self, locode_dict, subdiv_dict):
        key, item = list(locode_dict.items())[0]

        subdiv_code = '%s:%s' % (item['state'], item['subdivision_code'])
        subdiv_service = lambda st, sc: subdiv_dict[subdiv_code]
        lcde = locode.Locode(subdiv_service, key, **item)

        assert str(lcde) == key
        assert dict(lcde) == item

    def test_can_get_locode_function(self, locode_dict, subdiv_dict):
        key, item = list(locode_dict.items())[0]

        subdiv_code = '%s:%s' % (item['state'], item['subdivision_code'])
        subdiv_service = lambda st, sc: subdiv_dict[subdiv_code]
        lcde = locode.Locode(subdiv_service, key, **item)

        assert lcde.functions == ('1', '2', '3', '4', '5')
        assert not lcde.function_not_known
        assert lcde.has_port_function
        assert lcde.has_rail_terminal_function
        assert lcde.has_road_terminal_function
        assert lcde.has_airport_function
        assert lcde.has_postal_exchange_function
        assert not lcde.has_multimodal_functions
        assert not lcde.has_fixed_transport_function
        assert not lcde.has_inland_port_function
        assert not lcde.has_border_crossing

        assert lcde.function_score == 4.5
