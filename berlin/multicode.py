# -*- ocding: utf-8 -*-
"""LOCODE region parser.

Parser to turn input data into sets of LOCODEs

"""

from fuzzywuzzy import fuzz
import heapq
from math import sqrt
from rtree import index as rtree_index

class RegionParser:
    """Matches locations to a series of LOCODEs"""

    _scores = {
        'name match': 2,
        'direct match': 1,
        'component match': 0.5,
        'value match': 0.2,
        'fuzzy coefficient': 0.5,
        'function coefficient': 0.1
    }

    # In degrees
    _distance_threshold = 0.25

    def __init__(self, locode_dict, distances=True, distance_threshold=0.25):
        self._locode_dict = locode_dict
        self._locode_dict_by_name = {v.name: v for k, v in locode_dict.items()}
        self._locode_rtree = rtree_index.Index()
        self._locode_rtree_index = 0
        self._distance_threshold = distance_threshold

        if distances:
            for k, v in locode_dict.items():
                if v.coordinates:
                    x, y = v.coordinates
                    self._locode_rtree_index += 1
                    self._locode_rtree.insert(self._locode_rtree_index, (x, y, x, y), obj=k)

    def search(self, x, y, box_radius=None, nearest_only=True):
        if not box_radius:
            box_radius = self._distance_threshold

        if nearest_only:
            nearest_codes = self._locode_rtree.nearest((x, y, x, y), 1, objects=True)

            try:
                nearest_codes = [next(nearest_codes)]
            except StopIteration:
                return None, -1.
        else:
            nearest_codes = self._locode_rtree.intersection((x - box_radius, y - box_radius, x + box_radius, y + box_radius), objects=True)

        code_result = []
        for nearest in nearest_codes:
            lcde = self._locode_dict[nearest.object]
            distance = min(abs(x - lcde.coordinates[0]), abs(y - lcde.coordinates[1]))
            if distance <= box_radius:
                code_result.append((lcde, distance))

        if nearest_only:
            return code_result[0] if code_result else (None, -1.)

        return code_result

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
        del locode_fields['name']

        for field in set(comparators.keys()) & set(locode_fields.keys()):
            if locode_fields[field] != comparators[field]:
                return 0

        if 'name' in comparators:
            score_component = self._scores['name match'] * locode.name_score(comparators['name'])
            if log_steps is not None:
                log_steps.append(('NAME MATCH', score_component, comparators['name']))
            score += score_component

        #for field, value in locode_fields.items():
        #    if field in comparators:
        #        score += self._score_comparison(field, value, comparators[field], log_steps)
        #    elif value in comparators.values():
        #        score_component = self._scores['value match']
        #        if log_steps is not None:
        #            log_steps.append(('VALUE MATCH', score_component, field))
        #        score += score_component

        #comparator_string = ', '.join(comparators.values())

        #ratio = fuzz.token_set_ratio(comparator_string, locode.definition())
        #score_component = self._scores['fuzzy coefficient'] * ratio * 0.01
        #if log_steps is not None:
        #    log_steps.append(('FUZZY COEFFICIENT', score_component, ratio))
        #score += score_component

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
            if 'name' in comparators and 'supercode' in comparators and comparators['name'] in self._locode_dict_by_name:
                lcde = self._locode_dict_by_name[comparators['name']]
                if lcde.supercode == comparators['supercode']:
                    return lcde.identifier, lcde, 10., [('EXACT NAME MATCH',)]

            locode = max(self._locode_dict.items(), key=lambda v: self._score_match(comparators, v[1]))
            log_list = list()
            return locode[0], locode[1], self._score_match(comparators, locode[1], log_steps=log_list), log_list
        else:
            largest = heapq.nlargest(matches, self._locode_dict.items(), key=lambda v: self._score_match(comparators, v[1]))
            log_lists = {lcde[0]: list() for lcde in largest}
            return [(lcde[0], lcde[1], self._score_match(comparators, lcde[1], log_steps=log_lists[lcde[0]]), log_lists[lcde[0]]) for lcde in largest]
