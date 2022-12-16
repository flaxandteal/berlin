# -*- ocding: utf-8 -*-
"""Base code type.

This file contains a class for representing UN LOCODE related types.

"""

from fuzzywuzzy import fuzz
import re

# Should be great circle (esp if not small)
from math import sqrt


class Code:
    """Basic representation of codes"""

    _fields = ()
    _intrinsic_fields = ()
    _fixed_coordinates = None
    _barycentre = None
    function_score = 0
    code_type = None

    @classmethod
    def _code_service(cls, *args, **kwargs):
        raise RuntimeError("Code service not available for this code")

    def __init__(self, identifier, **kwargs):
        self.identifier = identifier
        self._definition = identifier
        self._children = []

        if 'code_service' in kwargs:
            self._code_service = kwargs['code_service']

        for field in self._fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])
            elif field in self._intrinsic_fields:
                setattr(self, field, None)

        self.alternative_names = []
        if 'name' in kwargs and kwargs['name']:
            self.alternative_names.append(kwargs['name'])
        if 'alternative_names' in kwargs and kwargs['alternative_names']:
            self.alternative_names += kwargs['alternative_names']
        if not self.alternative_names:
            print(identifier, kwargs)

    def __str__(self):
        return self.identifier

    def __repr__(self):
        minimal = '<bln|'
        if self.code_type:
            minimal += '{}#'.format(self.code_type)
        minimal += '{}'.format(self.identifier)
        if self.alternative_names:
            minimal += '|"{}"'.format(self.alternative_names[0])
        minimal += '>'
        return minimal

    def __iter__(self):
        for field in self._fields:
            value = self.get(field)
            if value:
                yield field, self.get(field)

    def get_children(self):
        return self._children

    def add_child(self, code):
        self._children.append(code)

        if code.coordinates:
            self._barycentre = None

    def name_score(self, test_name):
        """Get a score for the matching of a name."""

        if not test_name:
            return 0

        regex = re.compile(r'\b{}\b'.format(test_name), re.I)
        for name in self.alternative_names:
            if name == test_name:
                return 1.0
            if regex.search(name):
                return 0.9
            # It's less significant if our test name is a subset of
            # the code's name than the reverse
            if name in test_name:
                return max(0.9, 1.4 * len(name) / len(test_name))

        return 0.009 * max(map(lambda alt_name: fuzz.token_sort_ratio(test_name, alt_name), self.alternative_names))

    def as_pair(self):
        """Returns a pair that can be used to build a code dictionary."""
        return repr(self), dict(self)

    def describe(self):
        """Returns a more informative description of this item."""
        return "<BerlinCode [{}#{}] with {} fields>".format(self.code_type, str(self), dict(self))

    def get(self, attr):
        """Obtain field value or return None if it was not set."""
        return getattr(self, attr, None)

    def definition(self):
        """Returns a definition-type string."""
        return self._definition

    def distance(self, x, y):
        if self.coordinates:
            return sqrt((x - self.coordinates[0]) ** 2 + (y - self.coordinates[1]) ** 2)

    def paragraph(self):
        """Print a paragraph version of information about this code."""
        content = "%s\n[DE] %s\n[DF] %s\n" % (str(self), self.describe(), self.definition())

        for field, value in self:
            if value:
                content += "\n%s: %s" % (field.upper(), value)

        content += "\nALTERNATIVE NAMES: [%s]" % "] [".join(self.alternative_names)

        if self.coordinates:
            content += "'\n{%.4lf, %.4lf}\n" % tuple(self.coordinates)

        if self._children:
            content += f"\n[Children: {len(self._children)}]\n"

        return content

    def to_json(self):
        s, d = self.as_pair()
        return {
            '<c>': self.code_type,
            's': s,
            'i': self.identifier,
            'd': d
        }

    @classmethod
    def from_json(cls, jsn, code_service=None):
        kw = jsn['d']
        if 'code_service':
            kw['code_service'] = code_service
        return cls(jsn['i'], **kw)

    @property
    def coordinates(self):
        if self._fixed_coordinates:
            return self._fixed_coordinates

        if not self._barycentre:
            child_coords = [child.coordinates for child in self._children if child.coordinates]
            if child_coords:
                x = sum([cc[0] for cc in child_coords]) / len(child_coords)
                y = sum([cc[1] for cc in child_coords]) / len(child_coords)
                self._barycentre = (x, y)

        return self._barycentre
