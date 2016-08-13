# -*- ocding: utf-8 -*-
"""LOCODE region parser.

Parser to turn input data into sets of LOCODEs

"""

from fuzzywuzzy import fuzz
import heapq

class RegionParser:
    """Matches locations to a series of LOCODEs"""

    _scores = {
        'direct match': 1,
        'component match': 0.5,
        'value match': 0.2,
        'fuzzy coefficient': 0.5,
        'function coefficient': 0.1
    }

    def __init__(self, locode_dict):
        self._locode_dict = locode_dict

    def _score_comparison(self, field, value_1, value_2, log_steps):
        score = 0

        overlap = set(value_1.replace(',', '').split(' ')) & set(value_2.replace(',', '').split(' '))
        score_component = self._scores['component match'] * len(overlap)
        if log_steps is not None:
            log_steps.append(('COMPONENT MATCH', score_component, field, overlap))
        score += score_component

        ratio = fuzz.token_sort_ratio(value_1, value_2)
        score_component = self._scores['direct match'] * ratio * 0.01
        if log_steps is not None:
            log_steps.append(('DIRECT MATCH', score_component, field, ratio))
        score += score_component

        return score

    def _score_match(self, comparators, locode, log_steps=None):
        score = 0
        locode_fields = dict(locode)

        for field, value in locode:
            if field in comparators:
                score += self._score_comparison(field, value, comparators[field], log_steps)
            elif value in self._scores.values():
                score_component = self._scores['value match']
                if log_steps is not None:
                    log_steps.append(('VALUE MATCH', score_component, field))
                score += score_component

        comparator_string = ', '.join(comparators.values())

        ratio = fuzz.token_set_ratio(comparator_string, locode.definition())
        score_component = self._scores['fuzzy coefficient'] * ratio * 0.01
        if log_steps is not None:
            log_steps.append(('FUZZY COEFFICIENT', score_component, ratio))
        score += score_component

        score_component = self._scores['function coefficient'] * locode.function_score
        if log_steps is not None:
            log_steps.append(('FUNCTION COEFFICIENT', score_component, locode.function_score))
        score += score_component

        return score

    def match(self, locode, **comparators):
        log_list = list()
        return self._score_match(comparators, locode, log_steps=log_list), log_list

    def analyse(self, matches=1, **comparators):
        if matches == 1:
            locode = max(self._locode_dict.items(), key=lambda v: self._score_match(comparators, v[1]))
            log_list = list()
            return locode[0], locode[1], self._score_match(comparators, locode[1], log_steps=log_list), log_list
        else:
            largest = heapq.nlargest(matches, self._locode_dict.items(), key=lambda v: self._score_match(comparators, v[1]))
            log_lists = {lcde[0]: list() for lcde in largest}
            return [(lcde[0], lcde[1], self._score_match(comparators, lcde[1], log_steps=log_lists[lcde[0]]), log_lists[lcde[0]]) for lcde in largest]
