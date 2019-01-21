# -*- ocding: utf-8 -*-
"""Handling IATA airport data.

With thanks to the ourairports.com

"""

from . import code


class Iata(code.Code):
    """Representation of airports."""

    _fields = ('name', 'type', 'city', 'country', 'region', 'iata', 'y', 'x', 'elevation')
    _intrinsic_fields = ('city',)

    code_type = 'IATA'

    def definition(self):
        """Returns a definition-type string."""
        return "%s, %s" % (self.get('name'), self.get('iata'))

    def describe(self):
        """Returns a more informative description of this state."""
        return "<IATA [{}] for {}>".format(str(self), self.get('name'))
