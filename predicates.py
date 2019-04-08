_predicates = {
    "even": is_even,
    "odd": is_odd,
}
def check_predicate(name, val):
    return _predicates[name.lower()](val)


def is_even(val):
    return val % 2 == 0


def is_odd(val):
    return val % 2 == 1
