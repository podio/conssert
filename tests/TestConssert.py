from unittest import TestCase
import operator
from conssert import assertable


class TestConssert(TestCase):

    def setUp(self):
        self.rock_bands = [
            {
                "band": "Pink Floyd",
                "members": [
                    "Barret",
                    "Gilmour",
                    "Waters",
                    "Wright",
                    "Mason"
                ],
                "genre": "Psychedelic Rock",
                "albums": [
                    {
                        "title": "The piper at the gates of dawn",
                        "year": 1967,
                        "uk chart": None
                    },
                    {
                        "title": "The Wall",
                        "year": 1979,
                        "uk chart": 3
                    },
                    {
                        "title": "Animals",
                        "year": 1977,
                        "songs": [
                            "Pigs on the wing 1",
                            "Dogs",
                            "Pigs (three different ones)",
                            "Sheep",
                            "Pigs on the wing 2"
                        ],
                        "#tracks": 5
                    },
                    {
                        "title": "The dark side of the moon",
                        "certifications": {"Australia": "14x Platinum",
                                           "United Kingdom": "9x Platinum",
                                           "United States": "Diamond"}
                    }
                ],
                "periods": {
                    1963: "Formation",
                    1968: "Fame",
                    1978: "Waters leadership",
                    1986: "Gilmour leadership",
                    1995: "End",
                    2005: "Reunion"
                }
            },
            {
                "band": "Cream",
                "members": [
                    "Bruce",
                    "Clapton",
                    "Baker"
                ],
                "genre": "Blues Rock",
                "formation": 1966,
                "albums": [
                    {
                        "title": "Disraeli Gears"
                    }
                ]
            },
            {
                "band": "Deep Purple",
                "members": [
                    "Blackmore",
                    "Paice",
                    "Gillan"
                ],
                "genre": "Hard Rock",
                "formation": 1968,
                "albums": [
                    {
                        "title": "Made in Japan",
                        "year": 1972,
                        "songs": [
                            "Space truckin'",
                            "Smoke on the water"
                        ],
                        "#tracks": 7
                    },
                    {
                        "title": "Machine Head",
                        "length": 37.25,
                        "year": 1972,
                        "uk chart": 1
                    }
                ]
            }
        ]

        self.numbers = {"sequences": {"primes": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41],
                                      "Fibonacci": [1, 1, 2, 3, 5, 8, 13, 21, 34],
                                      "Padovan": [1, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12, 16, 21, 28, 37, 49],
                                      "Pell": [0, 1, 2, 5, 12, 29],
                                      "Perrin": [3, 0, 2, 3, 2, 5, 5, 7, 10, 12, 17, 22, 29, 39]}}

        self.programming_languages = {"functional": [{"Lisp": {"designer": {"name": "John McCarthy",
                                                                            "quote": "We understand human mental processes only slightly better than a fish understands swimming."},
                                                               "year": 58,
                                                               "features": ["macros", "recursion", "garbage collection"],
                                                               "type system": "dynamic"}},
                                                     {"Haskell": {"designer": {"name": "Simon Peyton Jones",
                                                                               "quote": "You'd like to be able to write a contract for a function like: 'You give me arguments that are bigger than zero and I'll give you a result that is smaller than zero'."},
                                                                  "year": 90,
                                                                  "features": ["lazy evaluation", "monads"],
                                                                  "type system": "static"}}],
                                      "procedural": [{"Fortran": {"designer": {"name": "John Backus",
                                                                               "quote": "Much of my work has come from being lazy."},
                                                                  "year": 57,
                                                                  "features": ["oldest high-level programming language",
                                                                               "high-performance computing"],
                                                                  "type system": "static"}},
                                                     {"C": {"designer": {"name": "Dennis Ritchie",
                                                                         "quote": "UNIX is basically a simple operating system, but you have to be a genius to understand the simplicity."},
                                                            "year": 72,
                                                            "features": ["weakly typing", "low level"],
                                                            "type system": "static"}}],
                                      "object oriented": [{"Python": {"designer": {"name": "Guido van Rossum",
                                                                                   "quote": "filter(P, S) is almost always written clearer as [x for x in S if P(x)]"},
                                                                      "year": 91,
                                                                      "features": ["duck typing", "multiple inheritance"],
                                                                      "type system": "dynamic"}},
                                                          {"Java": {"designer": {"name": "James Gosling",
                                                                                 "quote": "I think everybody has a different answer for what Web services are."},
                                                                    "year": 95,
                                                                    "features": ["JIT compiler", "type erasure"],
                                                                    "type system": "static"}}]}

    def test_basic_strings(self):
        with assertable("xyz") as in_str:
            in_str.one().has("xyz")
            in_str.one().has("x")
            in_str.one().is_("xyz")
            in_str.entire().is_("xyz")
            in_str.entire().has("xyz")
            in_str.no().is_("x")
            in_str.one("**").has("x")
            in_str.one("**").is_("xyz")
            self.assertRaises(AssertionError, in_str.one("*").has, "xyz")

        with assertable({"x": "yz"}) as in_str:
            for sel in ["x", "*", "**"]:
                in_str.one(sel).has("y")
                in_str.one(sel).has("y", "z")
                in_str.one(sel).has("yz")
                in_str.one(sel).is_("yz")
                in_str.no(sel).has("zy")

    def test_basic_numbers(self):
        with assertable(101) as in_number:
            in_number.one().has(101)
            in_number.one().is_(101)
            in_number.entire().is_(101)
            in_number.no().has(1)
            in_number.one("**").has(101)
            in_number.one("**").is_(101)

        with assertable({"x": 101}) as in_number:
            for sel in ["x", "*", "**"]:
                in_number.one(sel).has(101)
                in_number.one(sel).is_(101)
                in_number.no(sel).has(1)

    def test_basic_dicts(self):
        with assertable({"x": {"z1": 1,
                               "z2": 2},
                         "y": {"z3": 3,
                               "z4": 4}}) as in_dict:
            in_dict.one("x").is_({"z1": 1, "z2": 2})
            in_dict.entire("x").is_({"z1": 1, "z2": 2})
            in_dict.one("x").has({"z1": 1, "z2": 2})
            in_dict.one("x").has({"z1": 1}, {"z2": 2})
            in_dict.no("x").has([{"z1": 1}, {"z2": 2}])
            in_dict.one().has({"x": {"z1": 1, "z2": 2}})
            in_dict.one().has({"x": {"z1": 1, "z2": 2}}, {"y": {"z3": 3, "z4": 4}})
            in_dict.no().has([{"x": {"z1": 1, "z2": 2}}, {"y": {"z3": 3, "z4": 4}}])
            in_dict.one().is_({"x": {"z1": 1, "z2": 2}, "y": {"z3": 3, "z4": 4}})
            in_dict.one("*").has({"z1": 1}, {"z3": 3})
            in_dict.one("**").has(1, 2, 3, 4)
            in_dict.one("**").is_(4)
            in_dict.entire().is_({"x": {"z1": 1, "z2": 2}, "y": {"z3": 3, "z4": 4}})

    def test_basic_lists(self):
        with assertable([1, 2, 3]) as in_list:
            in_list.one().is_(1)
            in_list.one().has(2, 3)

        with assertable([1, 1, 1]) as in_list:
            in_list.every().is_(1)
            in_list.every().is_not(2)
            in_list.no().is_(2)

        with assertable([[1, 2, 3], [4, 5, 6]]) as in_list:
            in_list.some().has(1, 4)
            in_list.some().has([1, 2])
            in_list.no().has([1, 4])
            in_list.some().has([1, 2], [4, 5])

            in_list.no().is_([[5, 4, 6], [3, 2, 1]])
            in_list.no().is_([[4, 5, 6], [1, 2, 3]])
            in_list.one().is_([1, 2, 3])
            in_list.one().is_([6, 4, 5])

            in_list.entire().is_([[4, 5, 6], [1, 2, 3]])
            self.assertRaises(AssertionError, in_list.entire().is_, [[5, 4, 6], [3, 2, 1]])

        with assertable({"x": [1, 2, 3]}) as in_list:
            in_list.one("x").is_(2, 3)
            in_list.one("x").has(1, 2)
            in_list.no("x").has([1, 2])

        with assertable({"x": [1, 2, 3]}) as in_list:
            in_list.one("x").is_(3)

        with assertable([{"x": [1, 2, 3]}]) as in_list:
            in_list.one("x").is_([1, 2, 3])
            in_list.one("x").has([1, 2, 3])
            in_list.one("x").has([3, 2])
            in_list.one("x").has(1, 2)

        with assertable({"x": [1, 2, 3], "y": [4, 5, 6]}) as in_list:
            in_list.some("*").is_([3, 2, 1])
            in_list.some("*").is_([5, 4, 6])
            in_list.some("*").has([1, 2, 3])
            in_list.some("*").has([1, 2])
            in_list.some("*").has([1, 2], [5, 4])
            in_list.no("*").has([1, 2, 3, 4])
            in_list.one("*").has(1, 2)
            in_list.one("*").has(6)

        with assertable({"x": ["flat", "nested"]}) as in_str_list:
            in_str_list.one("x").has("fl", "ed")
            in_str_list.one("x").has("f", "d")  # catch!
            in_str_list.one("x").has(["f", "l"])
            in_str_list.one("x").has(["fl", "at"], ["nest"])
            in_str_list.no("x").has(["f", "d"])

        with assertable([{"x": [1, 2, 3]}]) as in_list:
            in_list.one("x").is_([1, 2, 3])
            in_list.one("*").is_([[1, 2, 3]])
            in_list.one("x").has([1, 2, 3])
            in_list.one("x").has([3, 2])
            in_list.one("x").has(1, 2)

        with assertable([[1, 2, 3], [4, 5, 6]]) as in_list:
            in_list.one().is_([1, 2, 3])

    def test_basic_nones(self):
        with assertable(None) as in_nones:
            in_nones.no().has_no_nones()

        with assertable([None, None, None, 1]) as in_nones:
            in_nones.some().has_no_nones()

        with assertable([1, 2, 5, 3, 4]) as in_nones:
            in_nones.every().has_no_nones()

        with assertable([1, 2, None, 3, 4]) as in_nones:
            self.assertRaises(AssertionError, in_nones.every().has_no_nones)

        with assertable({1: "z", 2: None}) as in_nones:
            self.assertRaises(AssertionError, in_nones.every("*").has_no_nones)

        with assertable({1: "z", 2: None}) as in_nones:
            self.assertRaises(AssertionError, in_nones.every("**").has_no_nones)

    def test_deeply_nested_has(self):
        with assertable({"n": {"e": {"s": {"t": {"e": "D"}}}}}) as in_deeply_nested:
            in_deeply_nested.one("n e s t e").has("D")

    def test_some_has(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.some("albums year").has(1972)

            in_rock_bands.some(["albums", "title"]).has("Made in Japan")
            in_rock_bands.some(["albums", "title"]).has("Made in Japan", "The Wall")
            self.assertRaises(AssertionError, in_rock_bands.some(["albums", "title"]).has, ["The Wall", "Animals"])

            in_rock_bands.some("members").has("Paice")
            in_rock_bands.some("members").has("Waters", "Barret")
            in_rock_bands.some("members").has(["Waters", "Barret"], ["Paice"])
            self.assertRaises(AssertionError, in_rock_bands.some("members").has, ["Waters", "Paice"])

            in_rock_bands.some().has({"band": "Pink Floyd"})
            in_rock_bands.some().has({"band": "Pink Floyd", "genre": "Psychedelic Rock"})
            in_rock_bands.some().has({"band": "Pink Floyd"}, {"genre": "Blues Rock"})
            self.assertRaises(AssertionError,  in_rock_bands.some().has, {"band": "Pink Floyd", "genre": "Blues Rock"})

    def test_every_has(self):
        with assertable(self.numbers) as in_numbers:
            in_numbers.every("sequences *").has(5)
            in_numbers.every("sequences *").has(2, 5)
            in_numbers.every("sequences *").has([2, 5])
            self.assertRaises(AssertionError,  in_numbers.every("sequences *").has, 0)

    def test_no_has(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.no("albums songs").has("Stairway to heaven")
            in_rock_bands.no("albums songs").has(["Stairway to heaven", "Smoke on the water"])
            self.assertRaises(AssertionError, in_rock_bands.no("albums songs").has,
                              "Stairway to heaven", "Smoke on the water")

    def test_other_combinations_has(self):
        with assertable(self.numbers) as in_numbers:
            in_numbers.one("sequences *").has(49)
            in_numbers.at_least(3, "sequences *").has(29)
            in_numbers.at_most(2, "sequences *").has(0)
            in_numbers.exactly(3, "sequences *").has(1)
            in_numbers.at_most(0, "**").has(42)

    def test_one_filter(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.one([("band", "Pink Floyd"), "periods", 1963]).has("Formation")
            in_rock_bands.one([("band", "Pink Floyd"), "periods"]).has({1963: "Formation", 2005: "Reunion"})
            in_rock_bands.one(["albums", ("title", "The Wall"), "year"]).is_(1979)
            in_rock_bands.one(["albums", ("title", "The Wall")]).has({"uk chart": 3})
            in_rock_bands.one(
                ["albums", ("title", "The dark side of the moon"), "certifications", "United States"]).has("Diamond")

    def test_some_has_some_of(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.some("albums year").has_some_of([1972, 2045])
            in_rock_bands.some("members").has_some_of(["Clapton", "Page"])

            in_rock_bands.one([("band", "Pink Floyd"), "periods", 1963]).has_some_of(["Formation", "Bazinga"])
            self.assertRaises(AssertionError,
                              in_rock_bands.one([("band", "Pink Floyd"), "periods", 1963]).has_some_of, "Formation", "!")

            in_rock_bands.one([("band", "Pink Floyd"), "periods"]).has_some_of({1963: "Formation", 2000: "!"})
            self.assertRaises(AssertionError,
                              in_rock_bands.one([("band", "Pink Floyd"), "periods"]).has_some_of, {1968: "!", 2000: "!"})

    def test_one_is(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.one("formation").is_(1968)
            in_rock_bands.one([("band", "Pink Floyd"), "periods"]).is_({1963: "Formation",
                                                                        1968: "Fame",
                                                                        1978: "Waters leadership",
                                                                        1986: "Gilmour leadership",
                                                                        1995: "End",
                                                                        2005: "Reunion"})
            in_rock_bands.one([("band", "Cream"), "members"]).has("Clapton")

            self.assertRaises(AssertionError, in_rock_bands.one([("band", "Cream"), "members"]).is_, "Clapton")
            self.assertRaises(AssertionError,
                              in_rock_bands.one([("band", "Pink Floyd"), "periods"]).is_, {1963: "Formation"})

            self.assertRaises(AssertionError,
                              in_rock_bands.one([("band", "Pink Floyd"), "periods"]).has, {1968: "Fame", 2000: "!"})

            self.assertRaises(AssertionError, in_rock_bands.one("albums year").is_, 1972)
            self.assertRaises(AssertionError, in_rock_bands.one("albums year").is_, 1973)

    def test_is_ordered(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.some("albums songs").is_(["Smoke on the water", "Space truckin'"])
            in_rock_bands.some("albums songs").is_(["Space truckin'", "Smoke on the water"])
            in_rock_bands.some("albums songs").is_ordered(["Space truckin'", "Smoke on the water"])
            self.assertRaises(AssertionError,
                              in_rock_bands.some("albums songs").is_ordered, ["Smoke on the water", "Space truckin'"])

        with assertable(self.numbers) as in_numbers:
            in_numbers.entire("sequences primes").is_([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41])
            in_numbers.entire("sequences Pell").is_([1, 2, 29, 5, 0, 12])

    def test_every_is_a(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.every("members").is_a(list)
            in_rock_bands.every_existent("albums year").is_a(int)
            in_rock_bands.every("genre").is_a(str)

    def test_is_nones(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.every("albums title").is_not_none()
            in_rock_bands.no("albums title").is_none()
            in_rock_bands.some(["albums", "uk chart"]).is_not_none()
            in_rock_bands.some(["albums", "uk chart"]).is_none()

    def test_is_not(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.one(["albums", ("title", "The Wall"), "year"]).is_not(1981)
            in_rock_bands.one(["albums", ("title", "The Wall"), "title"]).is_not("Other")

    def test_has_no_duplicates(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.some("albums year").has_no_duplicates()
            in_rock_bands.every("genre").has_no_duplicates()
            self.assertRaises(AssertionError, in_rock_bands.every_existent("albums year").has_no_duplicates)

            in_rock_bands.every("albums *").has_no_duplicates()
            self.assertRaises(AssertionError, in_rock_bands.every("albums **").has_no_duplicates)

        with assertable([1, 1, 1, 1, 1]) as in_ones:
            in_ones.at_least(1).has_no_duplicates()
            self.assertRaises(AssertionError, in_ones.at_least(2).has_no_duplicates)

    def test_has_no_nones(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.every_existent("albums year").has_no_nones()
            in_rock_bands.every().has_no_nones()

        with assertable(self.programming_languages) as in_languages:
            in_languages.every().has_no_nones()

    def test_has_not(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.every_existent("albums year").has_not(1984)
            in_rock_bands.every("genre").has_not("Rap")
            in_rock_bands.every_existent("periods").has_not({1984:"101"})
            self.assertRaises(AssertionError, in_rock_bands.every_existent("nonsense").has_not, "more nonsense")

    def test_matches(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.some("albums songs").matches("Pigs*", "Dogs*")
            self.assertRaises(AssertionError, in_rock_bands.some("albums songs").matches, "Horses*")
            in_rock_bands.every("genre").matches("\w\sRock")
            in_rock_bands.some("genre").matches("^Blues.*")
            self.assertRaises(AssertionError, in_rock_bands.every("genre").matches, "^Blues.*")

    def test_properties_comparators(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.some("members").has(5, cmp=operator.eq, property=len)
            in_rock_bands.every("members").has(3, cmp=operator.ge, property=len)
            in_rock_bands.every("genre").has("Rock", cmp=str.__contains__)

        with assertable(self.numbers) as in_numbers:
            in_numbers.every("**").has(50, cmp=operator.lt)
            in_numbers.one("sequences primes").has(0, cmp=operator.eq, property=lambda x: x % 2)
            in_numbers.every("sequences *").has(29, cmp=operator.ge, property=max)
            in_numbers.exactly(4, "sequences *").has(True, cmp=operator.eq, property=lambda x: x == sorted(x))

    def test_strictly_every(self):
        with assertable(self.rock_bands) as in_rock_bands:
            in_rock_bands.every("albums title").is_not_none()
            self.assertRaises(AssertionError, in_rock_bands.every, "albums songs")

    def test_expanded(self):
        with assertable(self.programming_languages) as in_languages:
            in_languages.one(["procedural", "Fortran", "type system"]).is_("static")
            in_languages.exactly(2, ["procedural", "*", "type system"]).is_("static")
            in_languages.at_least(2, "* * year").has(60, cmp=operator.lt)
            in_languages.some("* * * quote").matches("(?i)Unix")
            in_languages.every("**").has_no_nones()
            in_languages.every("functional **").has_no_duplicates()
            in_languages.every(["object oriented", "*", "*"]).has(4, cmp=operator.eq, property=len)

    def test_only_prefix_as_str(self):
        with assertable(self.rock_bands, "albums title") as in_album_titles:
            in_album_titles.some().is_("The Wall")
            in_album_titles.one().matches("Made in Ja")
            in_album_titles.no().has("Python")

    def test_prefix_as_str(self):
        with assertable(self.programming_languages, "functional Lisp") as in_lisp:
            in_lisp.one("year").is_(58)
            in_lisp.one(["designer", "name"]).is_("John McCarthy")

    def test_prefix_as_lst(self):
        with assertable(self.programming_languages, ["functional", "Lisp"]) as in_lisp:
            in_lisp.one("year").is_(58)
            in_lisp.one(["designer", "name"]).is_("John McCarthy")
