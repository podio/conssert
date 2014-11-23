"""
This module provides a context manager to perform validations on JSON-like data structures.
This is not intended to be used for schema validation, but rather for content assertion.

See examples in TestDemo.py and TestConssert.py

"""

import pprint
import re
import operator
import sys

from walker import walk

_identity = lambda x: x


class assertable:
    """ Context manager for object's content validation.
    """

    def __init__(self, data, prefix_path=[]):
        """
        Args:
            data (dict, list): object under test.
            prefix_path (str, list): path of the object tree under test.
        """
        # keep both args immutable
        self._data = data
        self._prefix_path = prefix_path if _list(prefix_path) else prefix_path.split()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, *path, **_):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(_split_and_reduce(path), min_checks=1, max_checks=2, wrap=True)
        return selector

    def every_existent(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for all the elements in the selection.
        It does not fail if the path does not exist for all the elements in the object tree.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(_split_and_reduce(path), min_checks=None)
        return selector

    def every(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for all the elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        The path must exists for all the elements in the object tree.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(_split_and_reduce(path), min_checks=None, force_path_present=True)
        return selector

    def exactly(self, num_checks, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for exactly num_checks elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(_split_and_reduce(path), min_checks=num_checks, max_checks=num_checks+1)
        return selector

    def at_least(self, num_checks, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for at least num_checks elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(_split_and_reduce(path), min_checks=num_checks)
        return selector

    def at_most(self, num_checks, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for at most num_checks elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(_split_and_reduce(path), max_checks=num_checks+1)
        return selector

    def one(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for exactly one elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        return self.exactly(1, _split_and_reduce(path))

    def some(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for at least one element in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        return self.at_least(1, _split_and_reduce(path))

    def no(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold false for all the elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        return self.at_most(0, _split_and_reduce(path))

    def _build_selector(self, path, min_checks=0, max_checks=sys.maxint, force_path_present=False, wrap=False):
        selection = assertable._selection(self._data, self._prefix_path + path, force_path_present)
        selector = _selector(selection=[selection] if wrap else selection,
                             path=self._prefix_path + path,
                             min_checks=assertable._min_checks(min_checks, selection),
                             max_checks=max_checks,
                             is_wrapped=wrap)
        return selector

    @staticmethod
    def _selection(obj, path, force_path_present, _root_path=None):
        if not path:
            return obj

        if _root_path is None:
            _root_path = path

        if _super_list(obj):
            return assertable._selection(_flatten(obj), path, force_path_present, _root_path)

        lookup_node, subpath = path[0], path[1:]
        if _tuple(lookup_node):
            (attr, value) = lookup_node
            return assertable._selection([item for item in obj if item[attr] == value],
                                            subpath, force_path_present, _root_path)
        else:
            try:
                return assertable._selection(
                    assertable._get(obj, lookup_node, force_path_present), subpath, force_path_present, _root_path)
            except KeyError:
                raise AssertionError("Attribute {} not found in path {}".format(lookup_node, _root_path))

    @staticmethod
    def _get(obj, lookup, force_path_present):
        if lookup == "**":
            return _expand_recursive(obj)

        if _dict(obj):
            if lookup == "*":
                return obj.values()
            elif force_path_present:
                return obj[lookup]
            else:
                return obj.get(lookup, [])
        else:
            if lookup == "*":
                return [item.values() for item in obj if _collection(obj)]
            else:
                traversable = lambda x, col: force_path_present or (_collection(col) and x in col)
                return [item[lookup] for item in obj if traversable(lookup, item)]

    @staticmethod
    def _min_checks(user_defined_min_checks, col):
        if user_defined_min_checks is not None:
            return user_defined_min_checks
        elif _list(col):
            return max(1, len(col))
        else:
            return 1


class _selector():

    def __init__(self,
                 selection,
                 path,
                 min_checks,
                 max_checks,
                 is_wrapped=False,
                 _root_min_check=None,
                 _root_max_check=None,
                 _root_selection=None,
                 ):
        self._selection = selection
        self._min_checks = min_checks
        self._max_checks = max_checks
        self._log_min_checks = min_checks if _root_min_check is None else _root_min_check
        self._log_max_checks = max_checks if _root_max_check is None else _root_max_check
        self._log_selection = selection if _root_selection is None else _root_selection
        self._log_path = path
        self._log_wrapped = is_wrapped

    @property
    def _first(self):
        if _list(self._selection) and len(self._selection) > 0:
            return self._selection[0]
        else:
            return self._selection

    @property
    def _rest(self):
        if _list(self._selection):
            return self._selection[1:]
        else:
            return []

    def _capture_err_state(self, val, custom_msg=""):
        raise AssertionError(
            """
            Selection on path {} --->

                    {}

            Compared with --->

                    {}

            Not verified (expected {}, got = {}) {}
            """.format(
                str(self._log_path) if self._log_path else "root",
                pprint.pformat(self._log_selection[0]) if self._log_wrapped and
                                                          len(self._log_selection) > 0
                                                    else pprint.pformat(self._log_selection),
                pprint.pformat(val),
                "< " + str(self._log_max_checks) if self._log_min_checks == 0 else "= " + str(self._log_min_checks),
                str(self._log_min_checks - self._min_checks),
                custom_msg))

    def has(self, *content, **options):
        """Compares content against the selection elements using the selector rules. If content is empty, do nothing.
        If an item in the content is a dict or a list, validation must succeed for every element in that item.

        Options:
            cmp: comparator function; e.g: operator.eq
            property: function applied to the selection element, the result of which will be passed to the
            comparator; e.g: len
        """
        for item in content:
            self._has(item, options.get("cmp"), options.get("property", _identity), raw_obj=item)

    def has_some_of(self, *content, **options):
        """Compares content against the selection elements using the selector rules. If content is empty, do nothing.
        If an item in the content is a dict or a list, validation must succeed for any element in that item.

        Options:
            cmp: comparator function; e.g: operator.eq
            property: function applied to the selection element, the result of which will be passed to the
            comparator; e.g: len
        """
        for item in content:
            self._has(item, options.get("cmp"), options.get("property", _identity), or_=True, raw_obj=item)

    def has_no_duplicates(self):
        """Asserts that there are no duplicates in the selection."""
        if self._min_checks > len(_unique(self._selection)):
            self._capture_err_state("[Itself]", "   ->   Duplicates found.")

    def has_no_nones(self):
        """Asserts that there are no nones in the selection."""
        self.has_not(None)

    def has_not(self, *content, **options):
        """Behaves like has(self, *content, **options) but succeeding only when validations hold false."""
        for item in content:
            compare = options.get("cmp") or _selector._default_comparator(self._first)
            negation_fn = _negate(compare)
            self._has(item, negation_fn, options.get("property", _identity), raw_obj=item)

    def has_length(self, content, **options):
        """Asserts the length of the selection."""
        self._has(content, options.get("cmp", operator.eq), len, raw_obj=content)

    def matches(self, *content):
        """Asserts that elements in selection match regular expressions in content."""
        regex_check_fn = lambda expr, pattern: \
            any([len(re.findall(pattern, item)) for item in expr]) if _list(expr) \
                else len(re.findall(pattern, expr)) > 0
        for regex in content:
            self._has(re.compile(regex), cmp_fn=regex_check_fn, raw_obj=regex)

    def is_ordered(self, *content):
        for item in content:
            self._has(tuple(item), cmp_fn=operator.eq, property_fn=lambda x: tuple(x), raw_obj=item)

    def is_(self, *content):
        """Asserts that elements in selection are equal to content. If list, order is not relevant."""
        for item in content:
            self._is(item, operator.eq)

    def is_a(self, obj):
        """Asserts the type of the elements in the selection."""
        self._is(obj, isinstance)

    def is_none(self):
        """Asserts that selection elements are none."""
        self.is_(None)

    def is_not_none(self):
        """Asserts that selection elements are not none."""
        self.is_not(None)

    def is_not(self, *content):
        """Asserts that elements in selection are not equal to content. If list, order is not relevant."""
        for item in content:
            self._is(item, operator.ne)

    def is_true(self):
        """Asserts that selection elements are True."""
        self._has(id(True), cmp_fn=operator.eq, property_fn=id, raw_obj=True)

    def is_false(self):
        """Asserts that selection elements are False."""
        self._has(id(False), cmp_fn=operator.eq, property_fn=id, raw_obj=False)

    def evals_true(self,):
        """Asserts that selection elements are logically True."""
        self._has(id(True), cmp_fn=operator.eq, property_fn=lambda x: id(bool(x)), raw_obj=True)

    def evals_false(self):
        """Asserts that selection elements are logically False."""
        self._has(id(False), cmp_fn=operator.eq, property_fn=lambda x: id(bool(x)), raw_obj=False)

    def _is(self, obj, cmp_fn):
        if _dict(obj):
            self._has(_unique(obj), cmp_fn=cmp_fn, property_fn=lambda dict_: _unique(dict_), raw_obj=obj)
        elif _list(obj):
            self._has(_unique(obj),
                      cmp_fn=cmp_fn,
                      property_fn=lambda list_: _unique(list_),
                      raw_obj=obj)
        else:
            self._has(obj, cmp_fn=cmp_fn, raw_obj=obj)

    def _has(self, obj, cmp_fn=None, property_fn=_identity, or_=False, raw_obj=None):
        if self._max_checks == 0:
            # raises assertion error
            self._capture_err_state(raw_obj or obj)

        if not self._selection and self._selection is not self._log_selection:
            # second condition ensure that it is "consuming" the selection and not testing against any logical false
            # expression (eg: [], None, 0...), in which case it should proceed with verification
            if self._min_checks > 0:
                # raises assertion error
                self._capture_err_state(raw_obj or obj)
            return

        if self._min_checks == 0 and _collection(self._selection) and self._max_checks > len(self._selection):
            return

        found = _selector._check(self._first, obj, cmp_fn, property_fn, or_)

        return _selector(selection=self._rest,
                         path=self._log_path,
                         min_checks=self._min_checks - found,
                         max_checks=self._max_checks - found,
                         is_wrapped=self._log_wrapped,
                         _root_min_check=self._log_min_checks,
                         _root_max_check=self._log_max_checks,
                         _root_selection=self._log_selection)._has(obj,
                                                                   cmp_fn=cmp_fn,
                                                                   property_fn=property_fn,
                                                                   or_=or_,
                                                                   raw_obj=raw_obj)

    @staticmethod
    def _check(selection_element, content_arg, cmp_fn, property_fn, or_):
        comparable = lambda *keys: property_fn(_recursive_get(selection_element, keys))
        compare = cmp_fn or _selector._default_comparator(selection_element)
        return _selector._check_element(content_arg, compare, comparable, or_)

    @staticmethod
    def _check_element(content_arg, compare, comparable, or_):
        fails = _negate(compare)
        if _list(content_arg):
            return _selector._check_list(content_arg, fails, comparable, or_, not or_)
        elif _dict(content_arg):
            return _selector._check_dict(content_arg, fails, comparable, or_, not or_)
        return _numeric_bool(compare(comparable(), content_arg))

    @staticmethod
    def _check_list(content_arg, fails, comparable, or_, and_):
        for element in content_arg:
            if fails(comparable(), element):
                if and_:
                    return 0
            elif or_:
                return 1
        return _numeric_bool(and_)

    @staticmethod
    def _check_dict(content_arg, fails, comparable, or_, and_):
        for key, value in content_arg.items():
            if _dict(value):
                return _selector._check_dict(value, fails, lambda *root_keys: comparable(key, root_keys), or_, and_)
            if fails(comparable(key), value):
                if and_:
                    return 0
            elif or_:
                return 1
        return _numeric_bool(and_)

    @staticmethod
    def _default_comparator(obj):
        if _list(obj):
            return list.__contains__
        elif _str(obj):
            return lambda str_, char: char == str_ if char is None else char in str_
        else:
            return operator.eq


def _list(obj):
    return isinstance(obj, list)


def _super_list(obj):
    return isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], list)


def _dict(obj):
    return isinstance(obj, dict)


def _tuple(obj):
    return isinstance(obj, tuple)


def _set(obj):
    return isinstance(obj, set)


def _str(obj):
    return isinstance(obj, basestring)


def _collection(obj):
    return _list(obj) or _dict(obj) or _tuple(obj)


def _numeric_bool(cond):
    return 1 if cond else 0


def _unique(col):
    if _dict(col):
        return _to_tuples_recursive(col.items())
    elif _list(col):
        return tuple(sorted(set(_to_tuples_recursive(col))))
    else:
        return col


def _to_tuples_recursive(col):
    if not _collection(col):
        return col
    elif _dict(col):
        return tuple(_to_tuples_recursive(item) for item in col.items())
    else:
        return tuple(_to_tuples_recursive(item) for item in col)


def _flatten(col):
    return [item for sublist in col for item in sublist]


def _negate(fn):
    return lambda *args: not fn(*args)


def _expand_recursive(obj):
    return [nodes[-1] for nodes in walk(obj) if nodes]


def _split_and_reduce(col):
    return sum(_split_strings(col), [])


def _split_strings(col):
    safe_split = lambda x: [] if x is None else x.split()
    return [item if _collection(item) else safe_split(item) for item in col]


def _recursive_get(dict_, keys):
    if not _dict(dict_) or not keys:
        return dict_
    if not _collection(keys):
        return dict_.get(keys)
    return _recursive_get(dict_.get(keys[0]), keys[-1])
