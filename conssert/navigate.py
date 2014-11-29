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
    safe_split = lambda x: [] if x is None else x.split()
    return [item if is_collection(item) else safe_split(item) for item in col]


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


def unique(col):
    """Returns the unique elements in col (recursive)"""
    if is_dict(col):
        return to_tuples(col.items())
    elif is_list(col):
        return tuple(sorted(set(to_tuples(col))))
    else:
        return col


def multi_get(dict_, keys):
    """Recursively looks up keys in dict_"""
    if not is_dict(dict_) or not keys:
        return dict_
    if not is_collection(keys):
        return dict_.get(keys)
    return multi_get(dict_.get(keys[0]), keys[-1] if len(keys) > 1 else None)


def walk(obj, _path_so_far=[]):
    """Returns a list of all the paths in the tree obj"""
    if isinstance(obj, list):
        return reduce(lambda accum, next_node: accum + walk(next_node, _path_so_far), obj, [])
    elif isinstance(obj, dict):
        return reduce(lambda accum, (current_node, next_node):
                      accum + walk(next_node, _path_so_far + [current_node]), obj.items(), [])
    return [_path_so_far + [obj]]


def expand_last_level(obj):
    """Returns a list of the leaf nodes in the tree obj"""
    return [nodes[-1] for nodes in walk(obj) if nodes]


def expand_one_level(obj):
    """Returns the next level of nodes in the tree obj"""
    if is_dict(obj):
        return obj.values()
    else:
        return [item.values() for item in obj if is_collection(obj)]
