conssert
========

Conssert is an ultralight Python library to facilitate the verification of arbitrarily complex data structures.

It provides a declarative syntax to navigate and lookup key/value pairs in nested data structures;
allowing partial assertions, conditional assertions, check certain properties, and more.

Conssert is designed for simplicity, robustness, and extensibility. Particularly, it avoids index lookups so you can
easily test changing data (e.g., integration tests with reusable fixtures or system tests that rely on external services).

Conssert is completely agnostic of the testing framework.

It is not a schema validation library. Although is possible to check types with it, Conssert
is intended for content verification.


### Usage.

Conssert verifications run within a context manager, which is initialized with the object under test:

```python
from conssert import assertable

def test_users(self):
    with assertable({'users': [
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
        users('users').has_length(3)
```

A Conssert verification has 2 parts. In the first part you get a selection of the object that you are interested in testing.
In the second part you assert certain values or properties. In the line above, `users('users')` returns a selection which
contains the value of the key 'users' and `.has_length(3)` asserts the length of that selection.
Similarly, you can write:

```python
        users.one('users name').is_('Alice')
        users.one('users name').is_('Alice', 'Bob')
```

The first verification asserts that there is exactly one user named 'Alice' and the second one asserts that there is
exactly one user named 'Alice' and exactly one other user (a different one) named 'Bob'.

You can also verify a subset of the properties:

```python
        users.one('users').has({'name': 'Alice', 'country': 'UK', 'favourite': {'color': 'Blue'}})
        users.one('users').has_some_of({'name': 'Alice', 'country': 'IE'}
```

The first verification runs an AND (there is a user named 'Alice', whose country is UK and whose favourite color is blue),
and the second one runs an OR (there is an user that either is named 'Alice' or her country is Ireland).

`users.one('users')` returns a selection containing the list of all users and will ensure that the assertion you perform
on will hold true for one and only one element in the selection. Similarly, `users.one('users name')` will return a
selection with all the user names, `users.one('users name favourite color')` will return all favourite colors from all the
users and so on.

Note that you can use a list (e.g., `users.one(['users', 'name', 'favourite', 'color'])`) and an arbitrary combination of
strings and lists (e.g., `users.one('users', ['name', 'favourite'], 'color'])`). All these expressions are equivalent and
it makes easy to reuse arguments.

An interesting Conssert feature is that you can filter the selection result by key/value pairs. Lets say that we are only
interested in Bob and we want to verify that he knows Python. We would write:

```python
        users.one(['users', ('name', 'Bob'), 'knows_python']).is_true()
```

You need to put a tuple in a list, where the first element of the tuple is the key and the second one is the value to filter.

This example also illustrates one verification method for the Boolean type (the other one, unsurprisingly is `is_false()`).
There are two other methods, namely `evals_true()` and `evals_false()` to verify the truth value of non Boolean types
(e.g., an empty sequence is False).

Lets see now how to verify lists.

```python
        users.one('users mails').has('bob@gmail.com')                             # exactly one user has this mail...
        users.one('users mails').has('bob@gmail.com', 'alice@gmail.com')          # different users has these 2 mails...
        users.one('users mails').has(['pythonlover@yahoo.com', 'bob@gmail.com'])  # the same user has these 2 mails
        users.one('users mails').has(['pythonlover@yahoo.com', 'bob@gmail.com'], 'alice@gmail.com')        # voila!
```

The examples above only perform partial verification. Normally you do partial verifications with `has` and full verifications
with `is_`. The `is_` method applied on lists doesn't care about ordering, but there is an order-relevant flavour of it:

```python
        # Bob has exactly these 2 mails
        users.one(['users', ('name', 'Bob'), 'mails']).is_(['pythonlover@yahoo.com', 'bob@gmail.com'])
        # Bob has exactly these 2 mails in that order
        users.one(['users', ('name', 'Bob'), 'mails']).is_ordered(['bob@gmail.com', 'pythonlover@yahoo.com'])
```

The only selectors used so far is `one` and the context manager itself, which happens to be a callable. We have used the
context manager callable at the beginning to verify the length of the object value.

The difference between `one` and the context manager callable is that the former iterates over the sequence of elements
performing a verification on each element and aggregating the results at the end, and the later performs only one
verification on the entire object (which might be a sequence or not).

There are other selectors that iterate over the sequence values. `every` will assert that the verification holds for all the
elements in the sequence:

```python
        users.every('users favourite number').is_a(int)
```

In the example above we make sure that all favourite numbers of all the users are values which type `int`.
If we are interested in both favourite numbers and favourite colors we can use the expansion symbol `*` to cover both:

```python
        users.every('users favourite *').evals_true()
```

This verifies that every value under the 'favourite' key for every user is logically true.
You also can expand all the leaves in the object tree:

```python
        users.every('**').is_not_none()  # every value of any property of any user is not none
```

So far we have been repeating the 'users' key in all our examples. We also can add it as a second argument in the context
manager initialization so all the "paths" in the selection arguments are prefixed by that one:

```python
        with assertable({'users': [
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
                               'number': 7}}]},
            'users') as users:
            users().has_length(3)  # we don't need to say users('users').has_length(3)
```

Even when we only have 3 users now, our user base might grow and we might prefer to say that there are at least 3 users
so we don't break our test if the data changes in the future.
The `has_length` method accepts a `cmp` argument in which you can specify a comparator function, so we could write:

```python
        users().has_length(3, cmp=operator.ge)  # 3 or more users
```

You can pass in any function that takes 2 arguments and return a Boolean value. You can use `cmp` with other methods too.
Actually, the previous example is the short form for:

```python
        users().has(3, cmp=operator.ge, property=len)
```

In here we have used a `cmp` and a `property` arguments. `property` is a function that will be applied to the selection element
*before* comparing to the input argument.


### Installation & Requirements.

Install with pip:

        pip install conssert

Alternately, you can clone it from the GitHub repo:

        git clone git@github.com:podio/conssert.git

Conssert depends on Python 2.7
