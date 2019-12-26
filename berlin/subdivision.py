# -*- ocding: utf-8 -*-
"""Handling ISO3166-2 subdivision data.

This module contains a class for representing UN LOCODE subdivisions.

"""

from . import code, state


class SubDivision(code.Code):
    """Representation of ISO3166-2 subdivisions."""

    _fields = ('name', 'supercode', 'subcode', 'level', 'state')

    function_score = 0.6

    code_type = 'ISO-3166-2'
    _fixed_coordinates = None
    _barycentre = None

    def __init__(self, *args, **kwargs):
        super(SubDivision, self).__init__(*args, **kwargs)

        ste = self.get('supercode')
        if state:
            self._state = self._code_service(ste, state.State.code_type)
        else:
            self._state = None

        self._definition = self._build_definition()

    def contains(self, lcde):
        """Check whether a locode lies in this region."""
        return any([l.identifier == lcde.identifier for l in self._children])

    def intersects(self, subdiv):
        """Check whether a subdivision intersects another."""
        raise NotImplementedError()

    def describe(self):
        """Returns a more informative description of this subdivision."""
        return "<SubDivision [{}] for {}>".format(str(self), self.get('name'))

    def definition(self):
        """Returns a definition-type string."""
        return self._definition

    def _build_definition(self):
        """Builds the definition-type string."""

        definition = []
        name = self.get('name')
        if name:
            definition.append(name)

        if self._state:
            definition.append(self._state.name)

        return ', '.join(definition)

    def get_state(self):
        return self._state

    def paragraph(self):
        content = super(SubDivision, self).paragraph()

        if self._state:
            subcontent = self._state.paragraph()
            content += "\n\n[State]\n"
            content += "\n".join(["    %s" % s for s in subcontent.split('\n')])

        return content
