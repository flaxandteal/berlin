# -*- ocding: utf-8 -*-
"""Handling GeoName data.

This module contains a class for representing GeoName data.

"""

from . import code


class State(code.Code):
    """Representation of ISO3166-1 states."""

    _fields = ('name', 'short', 'alpha2', 'official_en', 'official_fr', 'continent')

    def __init__(self, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)
        if not self.get('name'):
            self.name = self.get('short')

    def contains(self, lcde):
        """Check whether a locode lies in this region."""
        raise NotImplementedError()

    def definition(self):
        """Returns a definition-type string."""
        return "%s, %s" % (self.get('name'), self.get('alpha2'))

    def describe(self):
        """Returns a more informative description of this state."""
        return "<State [{}] for {}>".format(str(self), self.get('name'))
