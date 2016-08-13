import pytest

from berlin import multicode
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

@pytest.fixture
def subdivision_dict(state_dict):
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

    state_service = lambda st: state_dict[st]
    return {k: subdivision.SubDivision(state_service, k, **v) for k, v in subdiv_dict.items()}

@pytest.fixture
def locode_dict(subdivision_dict):
    flat_dict = {
        'BE:ANT': {
            'name': 'Antwerpen',
            'supercode': 'BE',
            'subcode': 'ANR',
            'subdivision_code': 'VAN',
            'state': 'BE'
        },
        'BE:ANH': {
            'name': 'Anhee',
            'supercode': 'BE',
            'subcode': 'ANH',
            'subdivision_code': 'WNA',
            'state': 'BE'
        }
    }

    ss = lambda st, sc: subdivision_dict['%s:%s' % (st, sc)]
    return {k: locode.Locode(ss, k, **v) for k, v in flat_dict.items()}


class TestMulticode:
    def test_can_parse_direct_name_match(self, locode_dict):
        parser = multicode.RegionParser(locode_dict)
        anhee = locode_dict['BE:ANH']
        locode = parser.analyse(name='Anhee')

        assert locode == ('BE:ANH', anhee)

    def test_can_parse_rotated_name_match(self, locode_dict):
        parser = multicode.RegionParser(locode_dict)
        anhee = locode_dict['BE:ANH']
        locode = parser.analyse(state='Anhee')

        assert locode == ('BE:ANH', anhee)

    def test_can_spot_similar_names(self, locode_dict):
        parser = multicode.RegionParser(locode_dict)
        antwerp = locode_dict['BE:ANT']
        locode = parser.analyse(name='Antwerp')

        assert locode == ('BE:ANT', antwerp)

    def test_can_spot_similar_names_with_diacritics(self, locode_dict):
        parser = multicode.RegionParser(locode_dict)
        anhee = locode_dict['BE:ANH']
        locode = parser.analyse(name='Anhée')

        assert locode == ('BE:ANH', anhee)
