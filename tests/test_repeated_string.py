import sys

sys.path.insert(0, "utils")

from processer import repeated_string


def test_not_deduplicated() -> None:
    assert repeated_string("hello world") == "hello world"


def test_deduplicated() -> None:
    assert repeated_string("hellohello") == "hello"


def test_empty_string() -> None:
    assert repeated_string("") == ""


def test_odd_length() -> None:
    assert repeated_string("abcab") == "abcab"


def test_whitespace_preserved() -> None:
    assert repeated_string("a b a b") == "a b a b"


def test_single_char() -> None:
    assert repeated_string("a") == "a"


def test_single_char_repeated() -> None:
    assert repeated_string("aa") == "a"


def test_unicode() -> None:
    assert repeated_string("ñoño") == "ño"


def test_whitespace_only() -> None:
    assert repeated_string("   ") == "   "
