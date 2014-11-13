def walk(obj, _path_so_far=[]):
    """Returns a list of all the paths in the object tree."""
    if isinstance(obj, list):
        return reduce(lambda accum, next_node: accum + walk(next_node, _path_so_far), obj, [])
    elif isinstance(obj, dict):
        return reduce(lambda accum, (current_node, next_node):
                        accum + walk(next_node, _path_so_far + [current_node]), obj.items(), [])
    return [_path_so_far + [obj]]