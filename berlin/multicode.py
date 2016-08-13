# -*- ocding: utf-8 -*-
"""LOCODE region parser.

Parser to turn input data into sets of LOCODEs

"""

from fuzzywuzzy import fuzz

class RegionParser:
    """Matches locations to a series of LOCODEs"""

    _scores = {
        'direct match': 1,
        'value match': 0.2,
        'fuzzy coefficient': 0.5
    }

    def __init__(self, locode_dict):
        self._locode_dict = locode_dict

    def _score_match(self, comparators, locode):
        score = 0
        locode_fields = dict(locode)
        for field, value in locode:
            if field in comparators:
                if comparators[field] == value:
                    score += self._scores['direct match']
            elif value in self._scores.values():
                score += self._scores['value match']

        comparator_string = ', '.join(comparators.values())
        score += self._scores['fuzzy coefficient'] * fuzz.token_set_ratio(comparator_string, locode.definition())
        return score

    def analyse(self, **comparators):
        return max(self._locode_dict.items(), key=lambda v: self._score_match(comparators, v[1]))
