# -*- coding: utf-8 -*-
"""
    chandas.padyas
    ~~~~~~~~~~~~~~

    Classes for representing various metrical forms.

    :license: MIT and BSD
"""

import re


class cached_property(object):

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        odict = obj.__dict__
        name = self.__name__
        if name not in odict:
            odict[name] = self.func(obj)
        return odict[name]


class Padya(object):

    """Abstract base class for a metrical form."""

    def __init__(self, name, pattern):
        #: The name of the meter.
        self.name = name

        #: The scan for each pāda.
        self.scans = [self._clean(pada) for pada in pattern]

        #: The number of syllables in the verse.
        self.num_syllables = sum(len(x) for x in self.scans)

    def __unicode__(self):
        return "<{}('{}')>".format(self.__class__.__name__, self.name)


class Vrtta(Padya):

    """Abstract class for syllabic meters."""

    @classmethod
    def _clean(self, data):
        return re.sub('[^LG.]', '', data)

    @classmethod
    def _padanta_laghu(self, scan):
        if scan.endswith(']'):
            return scan
        else:
            return scan[:-1] + '[LG]'

    @cached_property
    def regex(self):
        """Return a regex to test if some input matches the vrtta."""
        scans = [x.replace('.', '[LG]') for x in self.scans]
        regex_list = [scans[0], self._padanta_laghu(scans[1]),
                      scans[2], self._padanta_laghu(scans[3])]
        return re.compile(''.join(regex_list) + '$')

    @property
    def partial_regex(self):
        return self.regex


class Samavrtta(Vrtta):

    """Represents a type of sama-vṛtta."""

    def __init__(self, name, pattern):
        assert len(pattern) == 1
        Vrtta.__init__(self, name, pattern * 4)

    @cached_property
    def partial_regex(self):
        return re.compile(self._padanta_laghu(self.scans[0]))


class Ardhasamavrtta(Vrtta):

    """Represents a type of ardha-sama-vṛtta."""

    def __init__(self, name, pattern):
        assert len(pattern) == 2
        Vrtta.__init__(self, name, pattern * 2)

    @cached_property
    def partial_regex(self):
        return re.compile(self.scans[0] + self._padanta_laghu(self.scans[1]))


class Vishamavrtta(Vrtta):

    """Represents a type of viṣama-vṛtta."""

    def __init__(self, name, pattern):
        assert len(pattern) == 4
        Vrtta.__init__(self, name, pattern)


class Jati(Padya):

    """Abstract class for moraic meters."""

    def __init__(self, name, pattern, counts):
        Padya.__init__(self, name, pattern * 4)
        self.counts = counts
