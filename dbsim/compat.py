import sys
from numbers import Number

PY2 = sys.version_info[0] == 2

if PY2:
    string_types = basestring
else:
    string_types = str

# decorator for type to function mapping special cases
def per_type_cmp(type_):
    try:
        mapping = per_type_cmp.mapping
    except AttributeError:
        mapping = per_type_cmp.mapping = {}

    def decorator(cmpfunc):
        mapping[type_] = cmpfunc
        return cmpfunc

    return decorator


if PY2:

    def python2_sort_key(obj):
        return obj

else:

    class python2_sort_key(object):
        _unhandled_types = {complex}

        def __init__(self, ob):
            self._ob = ob

        def __lt__(self, other):
            self, other = self._ob, other._ob  # we don't care about the wrapper

            # default_3way_compare is used only if direct comparison failed
            try:
                return self < other
            except TypeError:
                pass

            # special casing for types
            for type_, special_cmp in per_type_cmp.mapping.items():
                if isinstance(self, type_) and isinstance(other, type_):
                    return special_cmp(self, other)

            # explicitly raise again, Python 2 won't sort these either
            if type(self) in python2_sort_key._unhandled_types:
                raise TypeError(
                    "no ordering relation is defined for {}".format(type(self).__name__)
                )
            if type(other) in python2_sort_key._unhandled_types:
                raise TypeError(
                    "no ordering relation is defined for {}".format(
                        type(other).__name__
                    )
                )

            # same type but no ordering defined, go by id
            if type(self) is type(other):
                return id(self) < id(other)

            # None always comes first
            if self is None:
                return True
            if other is None:
                return False

            # Sort by typename, but numbers are sorted before other types
            self_tname = "" if isinstance(self, Number) else type(self).__name__
            other_tname = "" if isinstance(other, Number) else type(other).__name__

            if self_tname != other_tname:
                return self_tname < other_tname

            # same typename, or both numbers, but different type objects, order
            # by the id of the type object
            return id(type(self)) < id(type(other))


@per_type_cmp(dict)
def dict_cmp(a, b):
    if len(a) != len(b):
        return len(a) < len(b)
    adiff = min(k for k in a if a.get(k) != b.get(k))
    bdiff = min(k for k in b if b.get(k) != a.get(k))
    if adiff != bdiff:
        return adiff < bdiff
    return a[adiff] < b[bdiff]
