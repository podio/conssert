from datetime import datetime
from unittest import TestCase
import operator
from conssert import Assertable


class TestDemo(TestCase):

    def setUp(self):
        self.programming_languages = \
[{'languages': {'academical': {'functional': [{'name': 'Lisp',
                                               'designer': {'name': 'John McCarthy',
                                                            'quote': """

                                                                 We understand human mental processes only slightly
                                                                        better than a fish understands swimming.

                                                                 """},
                                               'features': ['macros',
                                                            'recursion',
                                                            'garbage collection'],
                                               'type system': 'dynamic',
                                               'year': 1958},

                                              {'name': 'Haskell',
                                               'designer': {'name': 'Simon Peyton Jones',
                                                            'quote': """

                                                                    You'd like to be able to write a contract for
                                                                                    a function like:
                                                                 'You give me arguments that are bigger than zero and
                                                                   I'll give you a result that is smaller than zero'.

                                                                 """},
                                               'features': ['lazy evaluation',
                                                            'monads'],
                                               'type system': 'static',
                                               'year': 1990}]},

                'practical': {'functional': [{'name': 'Clojure',
                                              'designer': {'name': 'Rich Hickey',
                                                                       'quote': """

                                                                 Programming is not about typing... it's about thinking.

                                                                 """},
                                                          'features': ['software transactional memory',
                                                                       'multimethods',
                                                                       'protocols'],
                                                          'type system': 'dynamic',
                                                          'year': 2007}],

                              'object oriented': [{'name': 'Python',
                                                   'designer': {'name': 'Guido van Rossum',
                                                                'quote': """

                                                                 filter(P, S) is almost always written clearer as
                                                                               [x for x in S if P(x)]

                                                                 """},
                                                   'features': ['duck typing',
                                                                'GIL',
                                                                'multiple inheritance'],
                                                   'type system': 'dynamic',
                                                   'year': 1991},

                                                  {'name': 'Java',
                                                   'designer': {'name': 'James Gosling',
                                                                'quote': """

                                                                 I think everybody has a different answer for
                                                                             what Web services are.


                                                                 """},
                                                   'features': ['JIT compiler',
                                                                'generics'],
                                                   'type system': 'static',
                                                   'year': 1995}],

                              'procedural': [{'name': 'Fortran',
                                              'designer': {'name': 'John Backus',
                                                           'quote': """

                                                                 Much of my work has come from being lazy.

                                                                 """},
                                              'features': ['oldest high-level programming language',
                                                           'high-performance computing'],
                                              'type system': 'static',
                                              'year': 1957},

                                             {'name': 'C',
                                              'designer': {'name': 'Dennis Ritchie',
                                                           'quote': """

                                                                 UNIX is basically a simple operating system,
                                                                  but you have to be a genius to understand
                                                                                the simplicity.

                                                                 """},
                                              'features': ['weakly typing',
                                                           'low level'],
                                              'type system': 'static',
                                              'year': 1972}]}}}]

    def test_programming(self):
        with Assertable(self.programming_languages) as in_programming:
            # Something equals something
            in_programming.one(["languages", "academical", "functional", ("name", "Lisp"), "year"]).is_(1958)
            in_programming.some("languages academical functional year").is_(1990)
            self.assertRaises(AssertionError,
                              in_programming.every(["languages", "*", "functional", "type system"]).is_, "static")
            # Throws:
            #         AssertionError:
            #         Selection on the object under test with path ['languages', '*', 'functional', 'type system'] --->
            #
            #                 ['dynamic', 'static', 'dynamic']
            #
            #         Compared with assertion input --->
            #
            #                 'static'
            #
            #         Not verified (expected = 3, got = 1)
            in_programming.at_least(2, ["languages", "*", "functional", "type system"]).is_("dynamic")

            # Something contains something
            object_oriented_features = ["languages", "*", "object oriented", "features"]
            in_programming.some(object_oriented_features).has("duck typing")
            in_programming.some(object_oriented_features).has("duck typing", "generics")
            in_programming.some(object_oriented_features).has(["duck typing", "GIL"])
            self.assertRaises(AssertionError,
                              in_programming.some(object_oriented_features).has, ["duck typing", "generics"])
            #Throws:
            #       AssertionError:
            #       Selection on the object under test with path ['languages', '*', 'object oriented', 'features'] --->
            #
            #                 [['duck typing', 'GIL', 'multiple inheritance'], ['JIT compiler', 'generics']]
            #
            #       Compared with assertion input --->
            #
            #                 ['duck typing', 'generics']
            #
            #       Not verified (expected = 1, got = 0)
            in_programming.every(["languages", "*", "*", "type system"]).has("ic")
            in_programming.one(["languages", "practical", "procedural", ("name", "Fortran")]).has(
                                                                                            {"year": 1957,
                                                                                             "type system": "static"})
            in_programming.one(["languages", "practical", "procedural", ("name", "Fortran")]).has_some_of(
                                                                                    {"year": 2042,
                                                                                     "type system": "static"})

            # More on something equals something
            in_programming.some(object_oriented_features).is_(["JIT compiler", "generics"])
            in_programming.some(object_oriented_features).is_(["generics", "JIT compiler"])
            in_programming.some(object_oriented_features).is_ordered(["JIT compiler", "generics"])
            self.assertRaises(AssertionError,
                              in_programming.some(object_oriented_features).is_ordered, ["generics", "JIT compiler"])

            # Something compares somehow with some property of something else
            in_programming.exactly(2, "languages * * year").has(1960, cmp=operator.lt)
            in_programming("languages * * year").has(1957, cmp=operator.eq, property=min)
            in_programming.every("languages * * features").has(2, cmp=operator.ge, property=len)

            in_programming.some("languages practical functional").is_not_none()
            in_programming.every("languages **").is_not_none()

    def test_convenient_methods(self):
        with Assertable(self.programming_languages, "languages * *") as in_languages:
            in_languages.every("features").has_no_nones()
            in_languages.every("features").has_not("can fly")
            in_languages.every("features").has_not("can fly", "can drive")
            in_languages.every("year").has_not(datetime.now().year, cmp=operator.gt)
            in_languages.every("year").is_a(int)
            in_languages.no("designer name").is_("Jim Morrison")
            in_languages.at_most(1, "designer name").is_("Denis Ritchie")
            in_languages.at_most(1, "designer name").is_("Denis Ritchie", "James Gosling")
            in_languages.some("designer quote").matches("(?i)uNiX")
            in_languages.some("designer quote").matches("(?i)uNiX", "work.*lazy")
            in_languages.some(["designer"], "quote").matches("(?i)uNiX", "work.*lazy")

    def test_others(self):

        with Assertable([[1, 2, 3]]) as in_numbers:
            self.assertRaises(AssertionError, in_numbers.one().is_, [[1, 2, 3]])
            in_numbers.one().is_([1, 2, 3])
            in_numbers().is_([[1, 2, 3]])

        with Assertable([2, 3, 5, 7, 11, 13, 17, 19]) as in_primes:
            in_primes().has(True, cmp=operator.eq, property=lambda x: x == sorted(x))

            all_modulos = lambda x: [(n, x % n) for n in xrange(1, x + 1)]
            all_divisibles = lambda x: ([x for (x, m) in all_modulos(x) if m == 0], x)
            is_prime = lambda (div_set, x), _: len(div_set) == 2 and 1 in div_set and x in div_set
            in_primes.every().has("ignore this attribute", cmp=is_prime, property=all_divisibles)

        with Assertable([1, 2, 3, 3]) as in_some_duplicates:
            in_some_duplicates.at_least(3).has_no_duplicates()
            self.assertRaises(AssertionError,
                              in_some_duplicates.every().has_no_duplicates)
            self.assertRaises(AssertionError,
                in_some_duplicates().has, [1, 2, 3, 3], cmp=operator.eq, property=lambda x: list(set(x)))

        with Assertable({"programmers": [{"name": "Alice",
                                          "says": "I love functional programming!",
                                          "profession": "poet"},
                                         {"name": "Bob",
                                          "says": "I love monkey patching!",
                                          "profession": "plumber"},
                                         {"name": "Podio",
                                          "says": "I love agile!"}]}) as in_programmers:
            in_programmers.every_existent("programmers says").has("love")
            in_programmers.every("programmers says").has("love")
            self.assertRaises(AssertionError,
                              in_programmers.every, "programmers profession")
            # Throws:
            #   AssertionError: Attribute profession not found in path ['programmers', 'profession']
            in_programmers.every_existent("programmers profession").is_not_none()

            in_programmers.one(["programmers", ("name", "Bob"), "profession"]).is_("plumber")

            # This doesn't work:
            #in_programmers.one(["programmers", ("profession", "plumber"), "says"]).has("monkey")

    def test_users(self):
        with Assertable({'users': [
                {'name': 'Alice',
                 'mails': ['alice@gmail.com'],
                 'country': 'UK',
                 'knows_python': False,
                 'birth_date': datetime(1987, 01, 06),
                 'favourite': {'color': 'Blue',
                               'number': 1}},
                {'name': 'Bob',
                 'mails': ['bob@gmail.com', 'pythonlover@yahoo.com'],
                 'knows_python': True,
                 'birth_date': datetime(1982, 04, 22),
                 'favourite': {'color': 'Black',
                               'number': 42}},
                {'name': 'Mette',
                 'mails': [],
                 'country': 'DK',
                 'knows_python': True,
                 'birth_date': datetime(1980, 11, 11),
                 'favourite': {'color': 'Green',
                               'number': 7}}]}) as users:
            users('users').has_length(3)  # there are 3 users
            users.one(['users', 'name']).is_('Alice')  # exactly one user is named Alice
            users.one('users name').is_('Alice', 'Bob')  # exactly one user is named Alice and another one is Bob
            users.one('users').has({'name': 'Alice', 'country': 'UK', 'favourite': {'color': 'Blue'}})  # exactly one user has these properties...
            users.one('users').has_some_of({'name': 'Alice', 'country': 'IE'})  # exactly one user is either named Alice or comes from Ireland
            users.one(['users', ('name', 'Alice'), 'knows_python']).is_false()  # exactly one user named Alice does not know Python
            users.one('users mails').has('bob@gmail.com')  # exactly one user has this mail...
            users.one('users mails').has('bob@gmail.com', 'alice@gmail.com')  # different users has these 2 mails...
            users.one('users mails').has(['pythonlover@yahoo.com', 'bob@gmail.com'])  # the same user has these 2 mails
            users.one('users mails').has(['pythonlover@yahoo.com', 'bob@gmail.com'], 'alice@gmail.com')  # voila!
            users.one(['users', ('name', 'Bob'), 'mails']).is_(['pythonlover@yahoo.com', 'bob@gmail.com'])  # Bob has exactly these 2 mails
            users.one(['users', ('name', 'Bob'), 'mails']).is_ordered(['bob@gmail.com', 'pythonlover@yahoo.com'])  # Bob has exactly these 2 mails in that order
            users.every('users favourite number').is_a(int)  # every user's favourite number is an int
            users.every(['users', 'favourite'], 'number').is_a(int)  # the same - arguments values are concatenated
            users.every('users favourite *').evals_true()  # every user's favourite thing is logically true (not None, 0, empty...)
            users.every('**').is_not_none()  # every value of any property of any user is not none

        with Assertable({'users': [
                {'name': 'Alice',
                 'mails': ['alice@gmail.com'],
                 'country': 'UK',
                 'knows_python': False,
                 'birth_date': datetime(1987, 01, 06),
                 'favourite': {'color': 'Blue',
                               'number': 1}},
                {'name': 'Bob',
                 'mails': ['bob@gmail.com', 'pythonlover@yahoo.com'],
                 'knows_python': True,
                 'birth_date': datetime(1982, 04, 22),
                 'favourite': {'color': 'Black',
                               'number': 42}},
                {'name': 'Mette',
                 'mails': [],
                 'country': 'DK',
                 'knows_python': True,
                 'birth_date': datetime(1980, 11, 11),
                 'favourite': {'color': 'Green',
                               'number': 7}}]}, 'users') as users:
            users().has_length(3)  # there are 3 users
            users().has(3, cmp=operator.eq, property=len)  # there are 3 users, the long way
            users().has_length(1, cmp=operator.gt)  # there are more than 1 user
            users().has(1, cmp=operator.gt, property=len)  # there are more than 1 user, the long way
            users.some('knows_python').is_true()  # some users know Python
            users.no('favourite color').is_('Yellow')  # no users have yellow as favourite color
            users.every([('name', 'Bob'), 'mails']).matches("[^@]+@[^@]+\.[^@]+")  # every Bob's mail matches the regex
            users.every('mails').has_no_duplicates()  # there are no duplicate mails
            users.every_existent('country').evals_true()  # in every user that has a country, that country is logically true
            users.every('birth_date').has(20, cmp=operator.gt,   # all users are more than 20 years old
                                          property=lambda birth_date: (datetime.now() - birth_date).days / 365)
            users.some('country').is_not('DK')  # not all countries are DK

            # users.every('name').is_('Alice')
            # AssertionError:
            # Selection on the object under test with path ['users', 'name'] --->
            #
            #        ['Alice', 'Bob', 'Mette']
            #
            # Compared with assertion input --->
            #
            #        'Alice'
            #
            # Not verified (expected = 3, got = 1)

            with Assertable({'name': 'Alice',
                             'country': 'UK',
                             'knows_python': False}) as alice:
                alice().has_keys('name', 'country')  # these are keys present in the dict
                alice().keys_are(['name', 'country', 'knows_python'])  # these are *all* the keys in the dict
