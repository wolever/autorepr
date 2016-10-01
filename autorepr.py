import types
import string


def to_str(obj, encoding='utf-8', **encode_args):
    r"""
    Returns a ``str`` of ``obj``, encoding using ``encoding`` if necessary. For
    example::

        >>> some_str = b"\xff"
        >>> some_unicode = u"\u1234"
        >>> some_exception = Exception(u'Error: ' + some_unicode)
        >>> to_str(some_str)
        '\xff'
        >>> to_str(some_unicode)
        '\xe1\x88\xb4'
        >>> to_str(some_exception)
        'Error: \xe1\x88\xb4'
        >>> to_str([42])
        '[42]'

    See source code for detailed semantics.
    """
    # Note: On py3, ``b'x'.__str__()`` returns ``"b'x'"``, so we need to do the
    # explicit check first.
    if isinstance(obj, str):
        return obj

    # We coerce to unicode if '__unicode__' is available because there is no
    # way to specify encoding when calling ``str(obj)``, so, eg,
    # ``str(Exception(u'\u1234'))`` will explode.
    if isinstance(obj, unicode) or hasattr(obj, "__unicode__"):
        # Note: unicode(u'foo') is O(1) (by experimentation)
        return unicode(obj).encode(encoding, **encode_args)

    return str(obj)

def to_unicode(obj, encoding='utf-8', fallback='latin1', **decode_args):
    r"""
    Returns a ``unicode`` of ``obj``, decoding using ``encoding`` if necessary.
    If decoding fails, the ``fallback`` encoding (default ``latin1``) is used.

    Examples::

        >>> to_unicode(b'\xe1\x88\xb4')
        u'\u1234'
        >>> to_unicode(b'\xff')
        u'\xff'
        >>> to_unicode(u'\u1234')
        u'\u1234'
        >>> to_unicode(Exception(u'\u1234'))
        u'\u1234'
        >>> to_unicode([42])
        u'[42]'

    See source code for detailed semantics.
    """

    # Note: on py3, the `bytes` type defines an unhelpful "__str__" function,
    # so we need to do this check (see comments in ``to_str``).
    if not isinstance(obj, str):
        if isinstance(obj, unicode) or hasattr(obj, "__unicode__"):
            return unicode(obj)

        obj_str = str(obj)
    else:
        obj_str = obj

    try:
        return unicode(obj_str, encoding, **decode_args)
    except UnicodeDecodeError:
        return unicode(obj_str, fallback, **decode_args)

class SafeFormatter(string.Formatter):
    def __init__(self, coerce_func):
        self.coerce_func = coerce_func
        string.Formatter.__init__(self)

    def format_field(self, value, format_spec):
        res = string.Formatter.format_field(self, value, format_spec)
        return self.coerce_func(res)

safe_str_formatter = SafeFormatter(to_str)
safe_unicode_formatter = SafeFormatter(to_unicode)

def _autofmthelper(name, fmt, result_type, extra, postprocess=None):
    if isinstance(fmt, types.FunctionType):
        extra = fmt.extra
        fmt = fmt.fmt

    if result_type is unicode:
        safe_formatter = safe_unicode_formatter
        fmt = unicode(fmt)
    elif result_type is str:
        safe_formatter = safe_str_formatter
        fmt = str(fmt)
    elif result_type is repr:
        safe_formatter = None
        fmt = str(fmt)

    def fmtfunc(self):
        kwargs = extra and dict((k, v(self)) for (k, v) in extra.items())
        try:
            result = fmt.format(self=self, **kwargs)
        except UnicodeError:
            if safe_formatter is None:
                raise
            result = safe_formatter.format(fmt, self=self, **kwargs)
        if postprocess is not None:
            result = postprocess(self, result)
        return result

    fmtfunc.__name__ = name
    fmtfunc.fmt = fmt
    fmtfunc.extra = extra
    return fmtfunc

def autounicode(fmt, **kwargs):
    """ Returns a simple ``__unicode__`` function::

        >>> class Person(object):
        ...     name = "Alex"
        ...     __unicode__ = autounicode("{self.name}")
        ...
        >>> unicode(Person())
        u'Alex'
        >>>
        """
    return _autofmthelper("__unicode__", fmt, unicode, kwargs)

def autostr(fmt, **kwargs):
    """ Returns a simple ``__str__`` function::

        >>> class Person(object):
        ...     name = "Alex"
        ...     __str__ = autostr("{self.name}")
        ...
        >>> str(Person())
        'Alex'
        >>>
        """

    if isinstance(fmt, types.FunctionType):
        kwargs = fmt.extra
        fmt = fmt.fmt

    return _autofmthelper("__str__", fmt, str, kwargs)

def autorepr(fmt, **kwargs):
    """ Returns a simple ``__repr__`` function::

        >>> class Person(object):
        ...     name = "Alex"
        ...     __repr__ = autorepr(["name"])
        ...
        >>> repr(Person())
        "<__main__.Person name='Alex' at 0x...>"
        >>> class Timestamp(object):
        ...     time = 123.456
        ...     __repr__ = autorepr(["time:0.01f"])
        ...
        >>> repr(Timestamp())
        '<__main__.Timestamp time=123.5 at 0x...>'
        >>>
        >>> class Animal(object):
        ...     name = "Puppy"
        ...     __repr__ = autorepr(
        ...         "name={self.name!r} name_len={name_len!r}",
        ...          name_len=lambda self: len(self.name),
        ...     )
        ...
        >>> repr(Animal())
        "<__main__.Animal name='Puppy' name_len=5 at 0x...>"
        >>>
        """
    if isinstance(fmt, list):
        fmt_bits = []
        for name in fmt:
            attr, _, fmt_spec = name.partition(":")
            attr, _, fmt_conv = attr.partition("!")
            fmt_suffix = (
                ":%s" %(fmt_spec, ) if fmt_spec else
                "!%s" %(fmt_conv or "r", )
            )
            fmt_bits.append("%s={%s%s}" %(
                attr,
                attr if attr in kwargs else "self.%s" %(attr, ),
                fmt_suffix,
            ))
        fmt = " ".join(fmt_bits)

    return _autofmthelper("__repr__", fmt, repr, kwargs, lambda self, result: (
        "<%s.%s %s at 0x%x>" %(
            self.__class__.__module__,
            self.__class__.__name__,
            result,
            id(self),
        )
    ))


if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
