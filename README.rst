``autorepr``: makes civilized string representations
====================================================

Python makes it easy to make a class, but annoying to specify how that class is
represented as a string. Did you forget to reference ``self`` again? Probably.
Did you just spend an hour trying to remember how to handle unicode? Almost
certainly.

``autorepr`` lets you customize ``__repr__``, ``__str__``, and ``__unicode__``
methods in a single line each. They'll let you see any number of attributes,
just the way you want to see them.

With ``autorepr``, you get the repers you want, without worrying about the
fiddly bits (like encoding and decoding), leaving you to focus on your project.


Installation
------------

::

    $ pip install autorepr


Usage
-----

``autorepr`` consists of three functions. ``autorepr`` builds a Python-esque
``__repr__`` string by passing either a ``str.format``-style string, or a list
of attributes which should be included in a ``name=value`` list. The
``autostr`` and ``autounicode`` functions are similar, and will do their best
to avoid Unicode encoding / decoding errors.

.. code:: python

    >>> from autorepr import autorepr, autostr, autounicode
    >>> class Person(object):
    ...     name = u"Alex ☃"
    ...     height = 123.456
    ...
    ...     __repr__ = autorepr(["name", "height:0.1f"])
    ...     __str__ = autostr("{self.name} ({self.height:0.0f} cm)")
    ...     __unicode__ = autounicode(__str__)
    ...
    >>> p = Person()
    >>> repr(p)
    "<__main__.Person name=u'Alex \\u2603' height=123.5 at 0x...>"
    >>> unicode(p)
    u'Alex \u2603 (123 cm)'
    >>> str(p)
    'Alex \xe2\x98\x83 (123 cm)'


Notice that ``autostr`` and ``autounicode`` are intelligent about converting
their input to/from unicode (decoding/encoding as UTF-8) as necessary:

.. code:: python

    >>> p.name = u"unicode: ☃"
    >>> unicode(p)
    u'unicode: \u2603 (123 cm)'
    >>> str(p)
    'unicode: \xe2\x98\x83 (123 cm)'
    >>> p.name = 'utf-8 bytes: \xe2\x98\x83'
    >>> unicode(p)
    u'utf-8 bytes: \u2603 (123 cm)'
    >>> str(p)
    'utf-8 bytes: \xe2\x98\x83 (123 cm)'

*Note*: ``autostr`` and ``autorepr`` won't crash on invalid UTF-8 (for example,
if ``autounicode`` is asked to turn binary data into unicode), but the result
is *undefined* and may not be desirable.

Additional properties can be passed in as kwargs, which will be called with
the instance as a parameter:

.. code:: python

    >>> name_with_len = autostr("{self.name} length={len}",
    ...                         len=lambda self: len(self.name))
    ...
    >>> p.name = 'Alex'
    >>> name_with_len(p)
    'Alex length=4'

This works with ``autorepr``'s list mode too:

.. code:: python

    >>> repr_with_len = autorepr(["name", "len"],
    ...                          len=lambda self: len(self.name))
    ...
    >>> repr_with_len(p)
    "<__main__.Person name='Alex' len=4 at 0x...>"

If a regular format string is passed to ``autorepr``, it will use that instead
of the generated string:

.. code:: python

    >>> repr_with_str = autorepr("{self.name!r}")
    >>> repr_with_str(p)
    "<__main__.Person 'Alex' at 0x...>"

And of course, if you don't want your ``__repr__`` to be wrapped in
``<ClassName ...>``, you can use ``autostr``:

.. code:: python

    >>> repr_with_autostr = autostr("Person({self.name!r})")
    >>> repr_with_autostr(p)
    "Person('Alex')"


Format specifications can also be passed to ``autorepr`` if the default of
``!r`` is undesierable (for example, turncating floats):

.. code:: python

    >>> with_fmt_spec = autorepr(["duration:0.1f", "addr:x", "type!s"],
    ...                          duration=lambda x: 123.456,
    ...                          addr=lambda x: 0xabc123,
    ...                          type=lambda x: "foo")
    >>> with_fmt_spec(None)
    '<__builtin__.NoneType duration=123.5 addr=abc123 type=foo at 0x...>'
