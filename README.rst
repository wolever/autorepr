``autorepr``: makes civilized string representations
====================================================

.. image:: https://travis-ci.org/wolever/autorepr.svg?branch=master
    :target: https://travis-ci.org/wolever/autorepr

Now with Python 3 support!

Overview
--------

Python makes classes easy, but ``__repr__`` methods hard. Did you forget to
reference ``self`` again? Probably. Did have you thought to yourself "eh, this
class is real simple, it doesn't need a repr"? Without a doubt. Was production
taken down three times last week because your ``__str__`` returned unicode? ...
no? Maybe that's just me.

``autorepr`` makes it simple to build expressive, safe, and correct,
``__repr__``, ``__str__``, ``__unicode__``, and ``__bytes__`` methods in a
single line each.

With ``autorepr``, you get the repers you want, without worrying about the
fiddly bits (like encoding and decoding), leaving you to focus on your project:

.. code:: python

    >>> from autorepr import autorepr, autotext
    >>> class Person(object):
    ...     name = u"Alex ☃"
    ...     height = 123.456
    ...
    ...     __repr__ = autorepr(["name", "height:0.1f"])
    ...     __str__, __unicode__ = autotext("{self.name} ({self.height:0.0f} cm)")
    ...
    >>> p = Person()
    >>> repr(p)
    "<__main__.Person name=u'Alex \\u2603' height=123.5 at 0x...>"
    >>> unicode(p)
    u'Alex \u2603 (123 cm)'
    >>> str(p)
    'Alex \xe2\x98\x83 (123 cm)'


Installation
------------

::

    $ pip install autorepr


Usage
-----

``autorepr`` exposes two main functions:

- ``autorepr``, which builds a Python-esque ``__repr__`` string by passing
  either a ``str.format``-style string, or a list of attributes which should be
  included in a ``name=value`` list::

    autorepr(["name", "height:0.1f"]) -->
        "<pkg.Person name=u'Alex \u2603' height=123.5 at 0x...>"
    autorepr("{self.id} name={self.name!r}") -->
        "<pkg.Person 123 name=u'Alex \u2603' at 0x...>"

- ``autotext``, which uses ``autostr`` and ``autounicode`` to create
  ``__str__`` and ``__unicode__`` methods in a Python 2 + 3 friendly way::

    __str__, __unicode__ = autotext("{self.name} ({self.height!d} cm)") -->
        str: 'Alex \xe2\x98\x83 (123cm)'
        unicode: u'Alex \u2603 (123cm)'

And three secondary functions - ``autostr``, ``autounicode``, and
``autobytes`` - which build ``__str__``, ``__unicode__``, and ``__bytes__``
functions, respectively. The functions will do their best to avoid Unicode
encoding / decoding errors, and will generally Do The Right Thing, even if the
inputs aren't necessarily sensible.

Note: the examples shown here are Python 2, but everything works equally well
under Python 3.

.. code:: python

    >>> from autorepr import autorepr, autotext, autostr, autounicode
    >>> class Person(object):
    ...     name = u"Alex ☃"
    ...     height = 123.456
    ...
    ...     __repr__ = autorepr(["name", "height:0.1f"])
    ...     __str__, __unicode__ = autotext("{self.name} ({self.height:0.0f} cm)")
    ...
    >>> p = Person()
    >>> repr(p)
    "<__main__.Person name=u'Alex \\u2603' height=123.5 at 0x...>"
    >>> unicode(p)
    u'Alex \u2603 (123 cm)'
    >>> str(p)
    'Alex \xe2\x98\x83 (123 cm)'


Notice that ``autostr`` and ``autorepr`` (as called here through ``autotext``)
are intelligent about converting to/from unicode (decoding/encoding as UTF-8)
as necessary:

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

Additional properties can be passed in as ``kwargs``, which will be called with
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
``!r`` is undesirable (for example, truncating floats):

.. code:: python

    >>> with_fmt_spec = autorepr(["duration:0.1f", "addr:x", "type!s"],
    ...                          duration=lambda x: 123.456,
    ...                          addr=lambda x: 0xabc123,
    ...                          type=lambda x: "foo")
    >>> with_fmt_spec(None)
    '<....NoneType duration=123.5 addr=abc123 type=foo at 0x...>'
