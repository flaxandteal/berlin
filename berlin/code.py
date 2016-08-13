# -*- ocding: utf-8 -*-
"""Base code type.

This file contains a class for representing UN LOCODE related types.

"""

class Code:
    """Basic representation of codes"""

    _fields = ()

    def __init__(self, identifier, **kwargs):
        self.identifier = identifier
        self._definition = identifier
        for field in self._fields:
            if field in kwargs and kwargs[field]:
                setattr(self, field, kwargs[field])

    def __str__(self):
        return self.identifier

    def __iter__(self):
        for field in self._fields:
            value = self.get(field)
            if value:
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

    def definition(self):
        """Returns a definition-type string."""
        return self._definition

    def paragraph(self):
        """Print a paragraph version of information about this code."""
        content = "%s\n[DE] %s\n[DF] %s\n" % (str(self), self.describe(), self.definition())

        for field, value in self:
            if value:
                content += "\n%s: %s" % (field.upper(), value)

        return content
