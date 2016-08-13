# -*- ocding: utf-8 -*-
"""Base code type.

This file contains a class for representing UN LOCODE related types.

"""

class Code:
    """Basic representation of codes"""

    _fields = ()

    def __init__(self, identifier, **kwargs):
        self.identifier = identifier
        for field in self._fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])

    def __str__(self):
        return self.identifier

    def __iter__(self):
        for field in self._fields:
            yield field, self.get(field)

    def as_pair(self):
        """Returns a pair that can be used to build a code dictionary."""
        return str(self), dict(self)

    def describe(self):
        """Returns a more informative description of this item."""
        return "<Code [{}] with {} fields>".format(str(self), dict(self))

    def get(self, attr):
        """Obtain field value or return None if it was not set."""
        return getattr(self, attr, None)
