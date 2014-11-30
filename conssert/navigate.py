from collections import OrderedDict
from functools import partial


def T(type_, obj):
    """Returns True if obj is of type type_"""
    return isinstance(obj, type_)


is_list = partial(T, list)

is_dict = partial(T, dict)

is_tuple = partial(T, tuple)

is_set = partial(T, set)

is_str = partial(T, basestring)


def is_juicy_list(obj):
    """Returns True if obj is a non-empty list"""
    return obj and is_list(obj)


def is_super_list(obj):
    """Returns True if obj is a list of lists"""
    return is_juicy_list(obj) and is_list(obj[0])


def is_collection(obj):
    """Returns True if obj is a list, dict, tuple or set"""
    return is_list(obj) or is_dict(obj) or is_tuple(obj) or is_set(obj)


def flatten(lst):
    """Flattens lst_"""
    return [item for sublist in lst for item in sublist]


def negate(fn):
    """Returns the opposite Truth Value that fn would return"""
    return lambda *args: not fn(*args)


def split_strings(col):
    """Recursively split the strings in col"""
    maybe_split = lambda x: [] if x is None else x.split()
    return [item if is_collection(item) else maybe_split(item) for item in col]


def split_and_reduce(col):
    """Recursively splits and concatenate the strings in col"""
    return sum(split_strings(col), [])


def to_numeric_bool(cond, col=None):
    """If no col is supplied, returns 1 if cond is True or 0 otherwise.
       If col is supplied returns 1 if cond is True and all elements are True,
       or if cond is False and any of the elements is True.
       """
    if col:
        fn = all if cond else any
        return 1 if fn(col) else 0
    else:
        return 1 if cond else 0


def to_tuples(col):
    """Recursively creates a tuple from every element in col"""
    if not is_collection(col):
        return col
    elif is_dict(col):
        return tuple(to_tuples(item) for item in col.items())
    else:
        return tuple(to_tuples(item) for item in col)


def to_dict(obj):
    """Recursively creates a dict from obj attributes and its values"""
    if is_list(obj) or is_tuple(obj) or is_set(obj):
        return map(lambda x: to_dict(x), obj)
    elif hasattr(obj, '__dict__'):
        return dict([(k, to_dict(v)) for k, v in vars(obj).items()])
    elif is_dict(obj):
        return dict([(k, to_dict(v)) for k, v in obj.items()])
    else:
        return obj


def unique(col):
    """Returns the unique elements in col (recursive)"""
    unique_elements = to_tuples(col.items()) if is_dict(col) else set(to_tuples(col))
    return tuple(sorted(unique_elements))


def multi_get(dict_, keys):
    """Recursively looks up keys in dict_"""
    if not is_dict(dict_) or not keys:
        return dict_
    if not is_collection(keys):
        return dict_.get(keys)
    return multi_get(dict_.get(keys[0]), keys[-1] if len(keys) > 1 else None)


def walk(obj, unwrap_lists=True, _path_so_far=[]):
    """Returns a list of all the paths in the tree obj"""
    if is_dict(obj):
        return reduce(lambda accum, (current_node, next_node):
                      accum + walk(next_node, unwrap_lists, _path_so_far + [current_node]), obj.items(), [])
    elif is_list(obj) and unwrap_lists:
        return reduce(lambda accum, next_node: accum + walk(next_node, _path_so_far=_path_so_far), obj, [])
    else:
        maybe_sort = lambda obj_: sorted(obj) if is_list(obj_) else obj_
        return [_path_so_far + [maybe_sort(obj)]]


def expand_last_level(obj):
    """Returns a list of the leaf nodes in the tree obj"""
    return [nodes[-1] for nodes in walk(obj) if nodes]


def expand_one_level(obj):
    """Returns the next level of nodes in the tree obj"""
    if is_dict(obj):
        return obj.values()
    else:
        return [item.values() for item in obj if is_collection(obj)]


def diff(dict1, dict2):
    dict1_tree = walk(dict1, unwrap_lists=False)
    dict2_tree = walk(dict2, unwrap_lists=False)
    keys_dict1 = [e[:-1] for e in dict1_tree]
    keys_dict2 = [e[:-1] for e in dict2_tree]
    deletions = [x for x in dict1_tree if x[:-1] not in keys_dict2]
    additions = [x for x in dict2_tree if x[:-1] not in keys_dict1]
    modifications = [x for x in dict2_tree if x not in dict1_tree and x not in additions]
    return {'removed': deletions,
            'added': additions,
            'changed': modifications}