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

        state = self.get('state')
        if state:
            self._state = self._state_service(state)
        else:
            self._state = None

    def contains(self, lcde):
        """Check whether a locode lies in this region."""
        raise NotImplementedError()

    def intersects(self, subdiv):
        """Check whether a subdivision intersects another."""
        raise NotImplementedError()

    def describe(self):
        """Returns a more informative description of this subdivision."""
        return "<SubDivision [{}] for {}>".format(str(self), self.get('name'))
