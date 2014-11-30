from unittest import TestCase
from conssert import assertable
from navigate import *


class TestNavigate(TestCase):

    def test_obj_to_dict(self):
        class X:
            pass

        class Z:
            def __init__(self, arg):
                self.arg = arg

        x1 = X()
        x1.a = 1
        x1.b = "b"
        x1.c = [3, 4, 5]
        x1.d = {10: 100, 20: 200}

        x2 = X()
        x2.p = x1
        x2.q = [x1]
        x2.r = lambda _: _

        z = Z("z")
        z.u = {1: {10: {100: x1},
                   20: x2}}
        z.v = [x1, x2, x1]
        z.w = Z("w")
        z.y = (0, x2, 0)
        z.z = set([x1, x1])

        dicts = to_dict([z, x1])
        for w in walk(dicts, unwrap_lists=True):
            print w

        with assertable(dicts) as obj_as_dict:
            obj_as_dict.one(['u', 1, 10, 100, 'c']).has([4, 5, 3])
            obj_as_dict.one(['u', 1, 10, 100, 'c']).has([4, 5])
            obj_as_dict.one(['u', 1, 10, 100]).has({'c': [3, 4, 5]})
            obj_as_dict.one(['u', 1, 10, 100]).has({'a': 1,
                                                    'b': 'b',
                                                    'c': [3, 4, 5],
                                                    'd': {10: 100, 20: 200}})
            obj_as_dict.one(['u', 1, 20, 'q', 'a']).is_(1)
            obj_as_dict.one('w arg').is_('w')
            obj_as_dict.one('arg').is_('z')
            obj_as_dict.exactly(2, 'v c').has(3)
            obj_as_dict.one('y').has(0, {'r': {}})
            obj_as_dict.one('z b').evals_true()
