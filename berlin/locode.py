# -*- ocding: utf-8 -*-
"""Handling ISO3166-2 subdivision data.

This file contains a class for representing UN LOCODE subdivisions.

"""

from . import code, subdivision, iata, state

_functions = {
    '0': {'property': 'function_not_known', 'description': 'Function not known, to be specified', 'score': -1},
    '1': {'property': 'has_port_function', 'description': 'Port, as defined in Rec 16', 'score': 1},
    '2': {'property': 'has_rail_terminal_function', 'description': 'Rail Terminal', 'score': 1},
    '3': {'property': 'has_road_terminal_function', 'description': 'Road Terminal', 'score': 1},
    '4': {'property': 'has_airport_function', 'description': 'Airport', 'score': 1},
    '5': {'property': 'has_postal_exchange_function', 'description': 'Postal Exchange Office', 'score': 0.5},
    '6': {'property': 'has_multimodal_functions', 'description': 'Multimodal Functions (ICDs, etc.)', 'score': 0.5},
    '7': {'property': 'has_fixed_transport_function', 'description': 'Fixed Transport Functions (e.g. Oil platform)', 'score': 0.25},
    '8': {'property': 'has_inland_port_function', 'description': 'Inland Port', 'score': 1},
    'B': {'property': 'has_border_crossing', 'description': 'Border Crossing', 'score': 0.5},
}

class Locode(code.Code):
    """Basic LOCODE representation type"""

    _fields = ('name', 'supercode', 'subcode', 'subdivision_name', 'subdivision_code', 'function_code', 'iata_override', 'city')

    code_type = 'UN-LOCODE'

    def __init__(self, *args, **kwargs):
        super(Locode, self).__init__(*args, **kwargs)

        assert 'code_service' in kwargs

        subdiv_code = self.get('subdivision_code')
        state_code = self.get('supercode')

        if subdiv_code:
            unit = self._code_service('{}:{}'.format(state_code, subdiv_code), subdivision.SubDivision.code_type)
        else:
            unit = self._code_service(state_code, state.State.code_type)

        self._subdiv = unit if subdiv_code else None
        self._state = unit if not subdiv_code else None

        self._definition = self._build_definition()

        funcs = self.get('function_code')
        if funcs:
            self.functions = tuple([s for s in '012345678B' if s in funcs])
        else:
            self.functions = ()

        score = 0
        for func in _functions:
            setattr(self, _functions[func]['property'], func in self.functions)
            if func in self.functions:
                score += _functions[func]['score']
        self.function_score = score

        self.iata = None
        iata_override = self.get('iata_override')
        if iata_override:
            self.iata_code = iata_override
        elif self.get('has_airport_function'):
            self.iata_code = self.get('subcode')

            self.iata = self._code_service(self.iata_code, iata.Iata.code_type)
            if self.iata:
                self.city = self.iata.city
            else:
                self.iata_code = None

        if self._subdiv:
            self.subdivision_name = self._subdiv.name

        if 'coordinates' in kwargs and kwargs['coordinates']:
            self._fixed_coordinates = kwargs['coordinates']
        else:
            self._fixed_coordinates = None

        # The design of code is such that the code's structure
        # does not need to be known, so missing attributes
        # are not assigned.

        # However, some are essential for a type of code, to
        # be assumed as existing. These must be explicitly added
        if 'subdivision_code' not in kwargs:
            self.subdivision_code = None

    def inside(self, subdiv):
        """Check whether this LOCODE is in a subdivision."""

        return subdiv.contains(self)

    def describe(self):
        """Returns a more informative description of this LOCODE."""
        return "<LOCODE [{}] for {} F{:.1f}>".format(str(self), self.definition(), self.function_score)

    def definition(self):
        """Returns a definition-type string."""
        return self._definition

    def _build_definition(self):
        """Builds the definition-type string."""

        definition = []
        name = self.get('name')
        if name:
            definition.append(name)

        if self._subdiv:
            definition.append(self._subdiv.definition())

        return ', '.join(definition)

    def get_state(self):
        return self._state

    def get_subdivision(self):
        return self._subdiv

    def paragraph(self):
        content = super(Locode, self).paragraph()

        unit = self._subdiv if self._subdiv else self._state
        if unit:
            subcontent = unit.paragraph()
            content += "\n\n[Subdivision]\n"
            content += "\n".join(["    %s" % s for s in subcontent.split('\n')])

        if self.functions:
            content += "\n\n[Functions]\n"
            content += "\n".join([_functions[func]['description'] for func in self.functions])

        if self.iata:
            subcontent = self.iata.paragraph()
            content += "\n\n[IATA]\n"
            content += "\n".join(["    %s" % s for s in subcontent.split('\n')])

        return content
