#!/usr/bin/env python

import unittest
import pytest

from rapidfuzz.distance import JaroWinkler_cpp, JaroWinkler_py
from rapidfuzz import process_cpp, process_py


def scorer(scorer, s1, s2, **kwargs):
    score1 = scorer(s1, s2, **kwargs)
    score2 = process_cpp.extractOne(s1, [s2], processor=None, scorer=scorer, **kwargs)[
        1
    ]
    score3 = process_cpp.extract(s1, [s2], processor=None, scorer=scorer, **kwargs)[0][
        1
    ]
    score4 = process_cpp.cdist([s1], [s2], processor=None, scorer=scorer, **kwargs)[0][
        0
    ]
    score5 = process_py.extractOne(s1, [s2], processor=None, scorer=scorer, **kwargs)[1]
    score6 = process_py.extract(s1, [s2], processor=None, scorer=scorer, **kwargs)[0][1]
    score7 = process_py.cdist([s1], [s2], processor=None, scorer=scorer, **kwargs)[0][0]
    assert pytest.approx(score1, score2)
    assert pytest.approx(score1, score3)
    assert pytest.approx(score1, score4)
    assert pytest.approx(score1, score5)
    assert pytest.approx(score1, score6)
    assert pytest.approx(score1, score7)
    return score1


def jarowinkler_distance(s1, s2, **kwargs):
    sim1 = scorer(JaroWinkler_py.distance, s1, s2, **kwargs)
    sim2 = scorer(JaroWinkler_cpp.distance, s1, s2, **kwargs)
    sim3 = scorer(JaroWinkler_py.distance, s1, s2, **kwargs)
    sim4 = scorer(JaroWinkler_cpp.distance, s1, s2, **kwargs)
    assert pytest.approx(sim1, sim2)
    assert pytest.approx(sim1, sim3)
    assert pytest.approx(sim1, sim4)
    return sim1


def jarowinkler_similarity(s1, s2, **kwargs):
    sim1 = scorer(JaroWinkler_py.similarity, s1, s2, **kwargs)
    sim2 = scorer(JaroWinkler_cpp.similarity, s1, s2, **kwargs)
    sim3 = scorer(JaroWinkler_py.normalized_similarity, s1, s2, **kwargs)
    sim4 = scorer(JaroWinkler_cpp.normalized_similarity, s1, s2, **kwargs)
    sim5 = 1.0 - jarowinkler_distance(s1, s2, **kwargs)
    assert pytest.approx(sim1, sim2)
    assert pytest.approx(sim1, sim3)
    assert pytest.approx(sim1, sim4)
    assert pytest.approx(sim1, sim5)

    return sim1


class JaroWinklerTest(unittest.TestCase):
    def _jaro_winkler_similarity(self, s1, s2, result):
        self.assertAlmostEqual(jarowinkler_similarity(s1, s2), result, places=4)
        self.assertAlmostEqual(jarowinkler_similarity(s2, s1), result, places=4)

    def test_hash_special_case(self):
        self._jaro_winkler_similarity([0, -1], [0, -2], 0.66666)

    def test_edge_case_lengths(self):
        self._jaro_winkler_similarity("", "", 0)
        self._jaro_winkler_similarity("0", "0", 1)
        self._jaro_winkler_similarity("00", "00", 1)
        self._jaro_winkler_similarity("0", "00", 0.85)

        self._jaro_winkler_similarity("0" * 65, "0" * 65, 1)
        self._jaro_winkler_similarity("0" * 64, "0" * 65, 0.9969)
        self._jaro_winkler_similarity("0" * 63, "0" * 65, 0.9938)

        s1 = "10000000000000000000000000000000000000000000000000000000000000020"
        s2 = "00000000000000000000000000000000000000000000000000000000000000000"
        self._jaro_winkler_similarity(s1, s2, 0.97948)

        s1 = "00000000000000100000000000000000000000010000000000000000000000000"
        s2 = "0000000000000000000000000000000000000000000000000000000000000000000000000000001"
        self._jaro_winkler_similarity(s2, s1, 0.95333)

        s1 = "00000000000000000000000000000000000000000000000000000000000000000"
        s2 = (
            "010000000000000000000000000000000000000000000000000000000000000000"
            "00000000000000000000000000000000000000000000000000000000000000"
        )
        self._jaro_winkler_similarity(s2, s1, 0.85234)


if __name__ == "__main__":
    unittest.main()
