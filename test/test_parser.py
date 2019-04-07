from euclid.parser import Token, tokenize


def test_tokenize_short_sentence():
    tokens = list(tokenize("Let x be an integer."))

    assert len(tokens) == 6
    assert tokens[0] == Token("LET", "Let")
    assert tokens[1] == Token("SYMBOL", "x")
    assert tokens[2] == Token("BE", "be")
    assert tokens[3] == Token("A", "an")
    assert tokens[4] == Token("SYMBOL", "integer")
    assert tokens[5] == Token("DOT", ".")


def test_tokenize_keywords():
    tokens = list(tokenize("prove let where by be is a an"))

    assert len(tokens) == 8
    assert tokens[0] == Token("PROVE", "prove")
    assert tokens[1] == Token("LET", "let")
    assert tokens[2] == Token("WHERE", "where")
    assert tokens[3] == Token("BY", "by")
    assert tokens[4] == Token("BE", "be")
    assert tokens[5] == Token("BE", "is")
    assert tokens[6] == Token("A", "a")
    assert tokens[7] == Token("A", "an")


def test_tokenize_numbers():
    tokens = list(tokenize("0 1 697 24.837"))

    assert len(tokens) == 4
    assert tokens[0] == Token("NUMBER", 0)
    assert tokens[1] == Token("NUMBER", 1)
    assert tokens[2] == Token("NUMBER", 697)
    assert tokens[3] == Token("NUMBER", 24.837)
