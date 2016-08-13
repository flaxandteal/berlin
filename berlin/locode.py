# -*- ocding: utf-8 -*-
"""Handling ISO3166-2 subdivision data.

This file contains a class for representing UN LOCODE subdivisions.

"""

from . import code


class Locode(code.Code):
    """Basic LOCODE representation type"""

    _fields = ('name', 'supercode', 'subcode', 'subdivision_code', 'state')

    def __init__(self, subdivision_service, *args, **kwargs):
        self._subdivision_service = subdivision_service
        super(Locode, self).__init__(*args, **kwargs)

        subdiv_code = self.get('subdivision_code')
        state_code = self.get('state')
        unit = self._subdivision_service(state_code, subdiv_code)

        self._subdiv = unit if subdiv_code else None
        self._state = unit if not subdiv_code else None

        self._definition = self._build_definition()

    def inside(self, subdiv):
        """Check whether this LOCODE is in a subdivision."""

        return subdiv.contains(self)

    def describe(self):
        """Returns a more informative description of this LOCODE."""
        return "<LOCODE [{}] for {}>".format(str(self), self.definition())

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

    def paragraph(self):
        content = super(Locode, self).paragraph()

        unit = self._subdiv if self._subdiv else self._state
        if unit:
            subcontent = unit.paragraph()
            content += "\n".join(["    %s" % s for s in subcontent.split('\n')])

        return content
