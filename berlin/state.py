# -*- ocding: utf-8 -*-
"""Handling ISO3166-1 state data.

This module contains a class for representing UN LOCODE states.

"""

from . import code


class State(code.Code):
    """Representation of ISO3166-1 states."""

    _fields = ('name', 'short', 'alpha2', 'alpha3', 'official_en', 'official_fr', 'continent')

    code_type = 'ISO-3166-1'

    def __init__(self, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)
        if not self.get('name'):
            self.name = self.get('short')

    def contains(self, lcde):
        """Check whether a locode lies in this region."""
        raise NotImplementedError()

    def definition(self):
        """Returns a definition-type string."""
        return "%s, %s-%s" % (self.get('name'), self.get('alpha2'), self.get('alpha3'))

    def describe(self):
        """Returns a more informative description of this state."""
        return "<State [{}] for {}>".format(str(self), self.get('name'))
