# -*- ocding: utf-8 -*-
"""Handling IATA airport data.

With thanks to the openflights database!

"""

from . import code


class Iata(code.Code):
    """Representation of ISO3166-1 states."""

    _fields = ('name', 'city', 'country', 'iata', 'icao', 'y', 'x', 'elevation', 'timezone', 'dst', 'tz_id')

    def definition(self):
        """Returns a definition-type string."""
        return "%s, %s" % (self.get('name'), self.get('iata'))

    def describe(self):
        """Returns a more informative description of this state."""
        return "<IATA [{}] for {}>".format(str(self), self.get('name'))
