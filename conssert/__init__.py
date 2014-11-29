"""
This module provides a context manager to perform validations on complex data structures.
See examples in TestDemo.py
"""

import pprint
import re
import operator
import sys
from navigate import *

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
        self._prefix_path = prefix_path if is_list(prefix_path) else prefix_path.split()

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
        selector = self._build_selector(split_and_reduce(path), min_checks=1, max_checks=2, wrap=True)
        return selector

    def every_existent(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for all the elements in the selection.
        It does not fail if the path does not exist for all the elements in the object tree.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(split_and_reduce(path), min_checks=None)
        return selector

    def every(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for all the elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        The path must exists for all the elements in the object tree.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(split_and_reduce(path), min_checks=None, force_path_present=True)
        return selector

    def exactly(self, num_checks, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for exactly num_checks elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(split_and_reduce(path), min_checks=num_checks, max_checks=num_checks+1)
        return selector

    def at_least(self, num_checks, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for at least num_checks elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(split_and_reduce(path), min_checks=num_checks)
        return selector

    def at_most(self, num_checks, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for at most num_checks elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        selector = self._build_selector(split_and_reduce(path), max_checks=num_checks+1)
        return selector

    def one(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for exactly one elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        return self.exactly(1, split_and_reduce(path))

    def some(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold true for at least one element in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        return self.at_least(1, split_and_reduce(path))

    def no(self, *path):
        """Returns a selection/view of the assertable object specified by path. Validations performed on it must
        hold false for all the elements in the selection.
        path might be a string or a list of strings and/or tuples with 2 elements, namely a key and a value.
        If tuple, selection will be filtered by given key(s) and value(s).
        '*' in the path expands the next level in the selection, and '**' expands recursively.
        """
        return self.at_most(0, split_and_reduce(path))

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

        if is_super_list(obj):
            return assertable._selection(flatten(obj), path, force_path_present, _root_path)

        lookup_node, subpath = path[0], path[1:]
        if is_tuple(lookup_node):
            (attr, value) = lookup_node
            filtered_nodes = [item for item in obj if item[attr] == value]
            return assertable._selection(filtered_nodes, subpath, force_path_present, _root_path)

        else:
            try:
                next_nodes = assertable._get(obj, lookup_node, force_path_present)
                return assertable._selection(next_nodes, subpath, force_path_present, _root_path)
            except KeyError:
                raise AssertionError("Attribute {} not found in path {}".format(lookup_node, _root_path))

    @staticmethod
    def _get(obj, lookup, force_path_present):
        if lookup == "**":
            return expand_last_level(obj)

        elif lookup == "*":
            return expand_one_level(obj)

        elif is_dict(obj):
            return assertable._scan_dict(obj, lookup, force_path_present)

        else:
            return assertable._scan_undefined_type(obj, lookup, force_path_present)

    @staticmethod
    def _scan_dict(obj, lookup, force_path_present):
        return obj[lookup] if force_path_present else obj.get(lookup, [])

    @staticmethod
    def _scan_undefined_type(obj, lookup, force_path_present):
        traversable = lambda x, col: force_path_present or (is_collection(col) and x in col)
        return [item[lookup] for item in obj if traversable(lookup, item)]

    @staticmethod
    def _min_checks(user_defined_min_checks, col):
        if user_defined_min_checks is not None:
            return user_defined_min_checks
        elif is_list(col):
            return len(col)
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
        if is_juicy_list(self._selection):
            return self._selection[0]
        else:
            return self._selection

    @property
    def _rest(self):
        if is_list(self._selection):
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
        if self._min_checks > len(unique(self._selection)):
            self._capture_err_state("[Itself]", "   ->   Duplicates found.")

    def has_no_nones(self):
        """Asserts that there are no nones in the selection."""
        self.has_not(None)

    def has_not(self, *content, **options):
        """Behaves like has(self, *content, **options) but succeeding only when validations hold false."""
        for item in content:
            compare = options.get("cmp") or _selector._default_comparator(self._first)
            negation_fn = negate(compare)
            self._has(item, negation_fn, options.get("property", _identity), raw_obj=item)

    def has_length(self, content, **options):
        """Asserts the length of the selection."""
        self._has(content, options.get("cmp", operator.eq), len, raw_obj=content)

    def matches(self, *content):
        """Asserts that elements in selection match regular expressions in content."""
        regex_check_fn = lambda expr, pattern: \
            any([len(re.findall(pattern, item)) for item in expr]) if is_list(expr) \
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

    def _is(self, input_arg, cmp_fn):
        if is_collection(input_arg):
            # TODO validate tuples and sets
            self._has(unique(input_arg), cmp_fn=cmp_fn, property_fn=lambda col: unique(col), raw_obj=input_arg)
        else:
            self._has(input_arg, cmp_fn=cmp_fn, raw_obj=input_arg)

    def _has(self, input_arg, cmp_fn=None, property_fn=_identity, or_=False, raw_obj=None):
        if self._max_checks == 0:
            # raises assertion error
            self._capture_err_state(raw_obj or input_arg)

        if not self._selection and self._selection is not self._log_selection:
            # second condition ensure that it is "consuming" the selection and not testing against any logical false
            # expression (eg: [], None, 0...), in which case it should proceed with verification
            # TODO verify trivial cases (e.g. -> with...([]) as... evals false)
            if self._min_checks > 0:
                # raises assertion error
                self._capture_err_state(raw_obj or input_arg)
            return

        if self._min_checks == 0 and is_collection(self._selection) and self._max_checks > len(self._selection):
            return

        found = _selector._check(self._first, input_arg, cmp_fn, property_fn, or_)

        return _selector(selection=self._rest,
                         path=self._log_path,
                         min_checks=self._min_checks - found,
                         max_checks=self._max_checks - found,
                         is_wrapped=self._log_wrapped,
                         _root_min_check=self._log_min_checks,
                         _root_max_check=self._log_max_checks,
                         _root_selection=self._log_selection)._has(input_arg,
                                                                   cmp_fn=cmp_fn,
                                                                   property_fn=property_fn,
                                                                   or_=or_,
                                                                   raw_obj=raw_obj)

    @staticmethod
    def _check(current_selection_element, input_arg, cmp_fn, property_fn, or_):
        current_selection_comparable = lambda *keys: property_fn(multi_get(current_selection_element, keys))
        comparator = cmp_fn or _selector._default_comparator(current_selection_element)
        return _selector._check_element(input_arg, comparator, current_selection_comparable, or_)

    @staticmethod
    def _check_element(input_arg, comparator, current_selection_comparable, or_):
        fails = negate(comparator)
        if is_list(input_arg):
            return _selector._check_list(input_arg, fails, current_selection_comparable, or_, not or_)
        elif is_dict(input_arg):
            return _selector._check_dict(input_arg, fails, current_selection_comparable, or_, not or_)
        return to_numeric_bool(comparator(current_selection_comparable(), input_arg))

    @staticmethod
    def _check_list(input_arg, fails, current_selection_comparable, or_, and_):
        for element in input_arg:
            rs = _selector._cmp(fails, current_selection_comparable, or_, and_, element)
            if rs is not None:
                return rs
        return to_numeric_bool(and_)

    @staticmethod
    def _check_dict(input_arg, fails, current_selection_comparable, or_, and_):
        nested_dicts = dict(filter(lambda (_, v): is_dict(v), input_arg.items()))
        for input_key, input_value in filter(lambda (k, _): k not in nested_dicts, input_arg.items()):
            rs = _selector._cmp(fails, current_selection_comparable, or_, and_, input_value, input_key)
            if rs is not None:
                return rs
        dict_value_comparable = lambda ninput_key, *root_keys: current_selection_comparable(ninput_key, root_keys)
        nested_rs = map(lambda (nested_input_key, nested_input_value):
                        _selector._check_dict(nested_input_value,
                                              fails,
                                              partial(dict_value_comparable, nested_input_key),
                                              or_,
                                              and_),
                        nested_dicts.items())
        return to_numeric_bool(and_, nested_rs)

    @staticmethod
    def _cmp(fails, current_selection_comparable, or_, and_, current_input_val, key=None):
        current_selection_val = current_selection_comparable(key) if key is not None else current_selection_comparable()
        if fails(current_selection_val, current_input_val):
            if and_:
                return 0
        elif or_:
            return 1

    @staticmethod
    def _default_comparator(obj):
        if is_list(obj):
            return list.__contains__
        elif is_str(obj):
            return lambda str_, char: str_ == char if char is None else char in str_
        else:
            return operator.eq
