import json
import os
from .locode import Locode
from .subdivision import SubDivision
from .state import State
from .iata import Iata
from .backend_dict import BackendDict
from .multicode import RegionParser
from .code import Code
from .utils import cache_dir

CODE_TYPES = {
    Locode.code_type: Locode,
    State.code_type: State,
    SubDivision.code_type: SubDivision,
    Iata.code_type: Iata,
}

_code_bank = None


class CodeDecoder(json.JSONDecoder):
    """Decoder to JSON allowing for Codes"""

    @classmethod
    def set_service(cls, service):
        cls.service = service

    @classmethod
    def _dict_to_code(cls, dct):
        if '<c>' in dct:
            return CODE_TYPES[dct['<c>']].from_json(dct, code_service=cls.service)
        return dct

    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self._dict_to_code

        json.JSONDecoder.__init__(self, *args, **kwargs)


class CodeEncoder(json.JSONEncoder):
    """Encoder to JSON allowing for Codes"""

    def default(self, obj):
        if isinstance(obj, Code):
            return obj.to_json()

        return json.JSONEncoder.default(self, obj)


class CodeBankIO:
    @staticmethod
    def read(state_file, subdiv_file, iata_file, locode_file, build_combined=False):
        code_bank = CodeBank()

        CodeDecoder.set_service(code_bank.sget)

        with open(state_file, 'r') as f:
            state_dict = json.load(f, cls=CodeDecoder)
            code_bank.add_dict(State.code_type, state_dict)

        with open(subdiv_file, 'r') as f:
            subdiv_dict = json.load(f, cls=CodeDecoder)
            code_bank.add_dict(SubDivision.code_type, subdiv_dict)

        with open(iata_file, 'r') as f:
            iata_dict = json.load(f, cls=CodeDecoder)
            code_bank.add_dict(Iata.code_type, iata_dict)

        with open(locode_file, 'r') as f:
            locode_dict = json.load(f, cls=CodeDecoder)
            code_bank.add_dict(Locode.code_type, locode_dict)

        for code, subdiv in subdiv_dict.items():
            ste = subdiv.get_state()
            if ste:
                ste.add_child(subdiv)

        for code, lcde in locode_dict.items():
            subdiv = lcde.get_subdivision()
            if subdiv:
                subdiv.add_child(lcde)

        locode_dict_by_state = {}
        for lcde, code in locode_dict.items():
            if code.supercode not in locode_dict_by_state:
                locode_dict_by_state[code.supercode] = {}
            locode_dict_by_state[code.supercode][lcde] = code
        code_bank.add_dict(Locode.code_type, locode_dict_by_state, by_state=True)

        if build_combined:
            code_bank.build_combined()

        return code_bank

    @staticmethod
    def write(code_bank, prefix):
        with open('{}-state.json'.format(prefix), 'w') as f:
            json.dump(code_bank._bank[State.code_type], f, cls=CodeEncoder)
        with open('{}-subdivision.json'.format(prefix), 'w') as f:
            json.dump(code_bank._bank[SubDivision.code_type], f, cls=CodeEncoder)
        with open('{}-iata.json'.format(prefix), 'w') as f:
            json.dump(code_bank._bank[Iata.code_type], f, cls=CodeEncoder)
        with open('{}-locode.json'.format(prefix), 'w') as f:
            json.dump(code_bank._bank[Locode.code_type], f, cls=CodeEncoder)

class CodeBank:
    def __init__(self, state_dict=None, subdiv_dict=None, locode_dict=None, locode_dict_by_state=None, iata_dict=None, build_combined=False):
        self._bank = {
            SubDivision.code_type: subdiv_dict,
            State.code_type: state_dict,
            Locode.code_type: locode_dict,
            Iata.code_type: iata_dict,
            Locode.code_type + '|by-state': locode_dict_by_state,
            'combined': None
        }

        if build_combined:
            self.build_combined()

    def add_dict(self, code_type, dct, by_state=False):
        if by_state:
            code_type += '|by-state'
        self._bank[code_type] = dct

    def build_combined(self):
        self._bank['combined'] = self._bank[SubDivision.code_type].copy()
        self._bank['combined'].update(self._bank[Locode.code_type])
        self._bank['combined'].update(self._bank[State.code_type])

    def get_parser(self, code_type=None, state=None, distances=True):
        if code_type is None:
            assert 'combined' in self._bank
            dct = self._bank['combined']
        elif state:
            code_type += '|by-state'
            dct = self._bank[code_type][state]
        else:
            dct = self._bank[code_type]

        return RegionParser(dct, distances=distances)

    def sget(self, identifier, code_type=None, state=None):
        try:
            return self.get(identifier, code_type, state)
        except KeyError:
            return None

    def get(self, identifier, code_type=None, state=None):
        if not code_type:
            code_type = 'combined'
        if state:
            return self._bank[code_type + '|by-state'][state][identifier]
        return self._bank[code_type][identifier]

    def get_values(self, code_type=None):
        if not code_type:
            code_type = 'combined'
        return self._bank[code_type].values()

    def from_identifier(self, identifier):
        if '#' in identifier:
            code_type, identifier = identifier.split('#')
        else:
            code_type = Locode.code_type

        if code_type == Locode.code_type and ':' in identifier:
            state, lcde = identifier.split(':')
            if state in self._bank[code_type + '|by-state']:
                return self._bank[code_type + '|by-state'][state][identifier]

        return self._bank[code_type][identifier]

def get_code_bank(data_sources, progress_bar=False, build_combined=False, force_rebuild=False):
    global _code_bank

    backend = BackendDict()

    if _code_bank is None and not force_rebuild:
        try:
            _code_bank = CodeBankIO.read(
                os.path.join(cache_dir, 'berlin-state.json'),
                os.path.join(cache_dir, 'berlin-subdivision.json'),
                os.path.join(cache_dir, 'berlin-iata.json'),
                os.path.join(cache_dir, 'berlin-locode.json'),
                build_combined=build_combined
            )
        except FileNotFoundError:
            pass

    if _code_bank is None or force_rebuild:
        _code_bank = CodeBank(*backend.retrieve(data_sources, progress_bar=progress_bar), build_combined=build_combined)
        os.makedirs(os.path.join(cache_dir, 'berlin'), exist_ok=True)
        CodeBankIO.write(_code_bank, os.path.join(cache_dir, 'berlin'))

    return _code_bank
