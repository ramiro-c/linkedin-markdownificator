import sys
sys.path.insert(0, 'utils')

from processer import repeated_string


def test_not_deduplicated():
    assert repeated_string("hello world") == "hello world"


def test_deduplicated():
    assert repeated_string("hellohello") == "hello"


def test_empty_string():
    assert repeated_string("") == ""


def test_odd_length():
    assert repeated_string("abcab") == "abcab"


def test_whitespace_preserved():
    assert repeated_string("a b a b") == "a b a b"
