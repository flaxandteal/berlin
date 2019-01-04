# -*- ocding: utf-8 -*-
"""Base code type.

This file contains a class for representing UN LOCODE related types.

"""

from fuzzywuzzy import fuzz
import re

class Code:
    """Basic representation of codes"""

    _fields = ()
    function_score = 0
    coordinates = None

    def __init__(self, identifier, **kwargs):
        self.identifier = identifier
        self._definition = identifier
        for field in self._fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])

        self.alternative_names = []
        if 'name' in kwargs and kwargs['name']:
            self.alternative_names.append(kwargs['name'])
        if 'alternative_names' in kwargs and kwargs['alternative_names']:
            self.alternative_names += kwargs['alternative_names']
        if not self.alternative_names:
            print(identifier, kwargs)

    def __str__(self):
        return self.identifier

    def __iter__(self):
        for field in self._fields:
            value = self.get(field)
            if value:
                yield field, self.get(field)

    def name_score(self, test_name):
        """Get a score for the matching of a name."""

        regex = re.compile(r'\b{}\b'.format(test_name), re.I)
        for name in self.alternative_names:
            if name == test_name:
                return 1.0
            if regex.search(name):
                return 0.9

        return 0.009 * max(map(lambda alt_name: fuzz.token_sort_ratio(test_name, alt_name), self.alternative_names))

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

        content += "\nALTERNATIVE NAMES: [%s]" % "] [".join(self.alternative_names)

        return content
