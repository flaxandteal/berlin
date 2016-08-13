# -*- ocding: utf-8 -*-
"""Handling ISO3166-1 state data.

This module contains a class for representing UN LOCODE states.

"""

from . import code


class State(code.Code):
    """Representation of ISO3166-1 states."""

    _fields = ('name', 'alpha2')

    def contains(self, lcde):
        """Check whether a locode lies in this region."""
        raise NotImplementedError()

    def definition(self):
        """Returns a definition-type string."""
        return "%s, %s" % (self.get('name'), self.get('alpha2'))

    def describe(self):
        """Returns a more informative description of this state."""
        return "<State [{}] for {}>".format(str(self), self.get('name'))
