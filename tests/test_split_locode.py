import pytest

from berlin import multicode

@pytest.fixture
def locode_dict():
    return {
        'DB:BE' {
            'Code': 'DE',
            'SubCode': 'BE',
            'Name': 'Berlin',
            'Type': 'Länder'
        }
    }


class TestMulticode:
    def test_can_parse_direct_name_match(self, locode_dict):
        parser = RegionParser()
        berlin = locode_dict['DB:BE']
        parser.initiate(locode_dict)
        locode = parser.analyse(name='Berlin')

        assert locode == berlin
