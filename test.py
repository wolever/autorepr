# -*- coding: utf-8 -*-

import os
import doctest

from nose.tools import assert_equal
from nose_parameterized import parameterized

from autorepr import autostr, autounicode, autorepr

class Person(object):
    def __init__(self, name):
        self.name = name


ascii = Person("Alex")
uni = Person(u"☃")
bin = Person("\x00\xff")

@parameterized([
    (ascii.name, autostr, ascii),
    (unicode(ascii.name), autounicode, ascii),
    (uni.name.encode("utf-8"), autostr, uni),
    (uni.name, autounicode, uni),
    (bin.name, autostr, bin),
    (u"\x00\xff", autounicode, bin),
])
def test_encodings(expected, func, input):
    f = func("{self.name}")
    res = f(input)
    assert_equal(res, expected)
    assert_equal(type(res), type(expected))


@parameterized([
    ("'Alex'", autorepr("{self.name!r}")),
    ("name='Alex'", autorepr(["name"])),
    ("42", autorepr("{foo}", foo=lambda self: 42)),
    ("name='Alex' foo=42", autorepr(["name", "foo"], foo=lambda self: 42)),
])
def test_autorepr(expected, func):
    res = func(ascii)
    assert_equal("<%s.Person %s at 0x%x>" %(__name__, expected, id(ascii)), res)


def test_with_function_as_input():
    f = autounicode(autostr("{self.name} {foo}", foo=lambda x: 42))
    assert_equal(f(ascii), "Alex 42")

def test_readme_doctests():
    res = doctest.testfile("README.rst", optionflags=doctest.ELLIPSIS, encoding="utf-8")
    assert_equal(res.failed, 0)


if __name__ == '__main__':
    import nose
    nose.run(argv=[__file__])
