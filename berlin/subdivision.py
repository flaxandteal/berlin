# -*- ocding: utf-8 -*-
"""Handling ISO3166-2 subdivision data.

This module contains a class for representing UN LOCODE subdivisions.

"""

from . import code


class SubDivision(code.Code):
    """Rpresentation of ISO3166-2 subdivisions."""

    _fields = ('name', 'supercode', 'subcode', 'level', 'state')

    def __init__(self, state_service, *args, **kwargs):
        self._state_service = state_service
        super(SubDivision, self).__init__(*args, **kwargs)

        state = self.get('supercode')
        if state:
            self._state = self._state_service(state)
        else:
            self._state = None

        self._definition = self._build_definition()

    def contains(self, lcde):
        """Check whether a locode lies in this region."""
        raise NotImplementedError()

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

    def paragraph(self):
        content = super(SubDivision, self).paragraph()

        if self._state:
            subcontent = self._state.paragraph()
            content += "\n".join(["    %s" % s for s in subcontent.split('\n')])

        return content
