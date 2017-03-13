from __future__ import print_function

import sys
import types
import string

def show_py2(x):
    if isinstance(x, unicode):
        print(repr(x))
    elif isinstance(x, str):
        print('b' + repr(x))
    else:
        print(x)

def show_py3(x):
    if isinstance(x, str):
        print('u' + ascii(x))
    else:
        print(x)

if sys.version_info < (3, 0, 0):
    PY2 = True
    text = unicode
    bytes = str
    dundertext_name = "__unicode__"
    dunderbytes_name = "__str__"
    show = show_py2
else:
    PY2 = False
    text = str
    bytes = bytes
    dundertext_name = "__str__"
    dunderbytes_name = "__bytes__"
    show = show_py3

PY3 = not PY2


def to_bytes(obj, encoding='utf-8', **encode_args):
    r"""
    Returns a ``str`` of ``obj``, encoding using ``encoding`` if necessary. For
    example::

        >>> some_str = b"\xff"
        >>> some_unicode = u"\u1234"
        >>> some_exception = Exception(u'Error: ' + some_unicode)
        >>> show(to_bytes(some_str))
        b'\xff'
        >>> show(to_bytes(some_unicode))
        b'\xe1\x88\xb4'
        >>> show(to_bytes(some_exception))
        b'Error: \xe1\x88\xb4'
        >>> show(to_bytes([42]))
        b'[42]'

    See source code for detailed semantics.
    """
    # Note: On py3, ``b'x'.__str__()`` returns ``"b'x'"``, so we need to do the
    # explicit check first.
    if isinstance(obj, bytes):
        return obj

    # We coerce to unicode if '__unicode__' is available because there is no
    # way to specify encoding when calling ``str(obj)``, so, eg,
    # ``str(Exception(u'\u1234'))`` will explode.
    if isinstance(obj, text) or hasattr(obj, dundertext_name):
        # Note: unicode(u'foo') is O(1) (by experimentation)
        return text(obj).encode(encoding, **encode_args)

    return bytes(obj)

def to_text(obj, encoding='utf-8', fallback='latin1', **decode_args):
    r"""
    Returns a ``unicode`` of ``obj``, decoding using ``encoding`` if necessary.
    If decoding fails, the ``fallback`` encoding (default ``latin1``) is used.

    Examples::

        >>> show(to_text(b'\xe1\x88\xb4'))
        u'\u1234'
        >>> show(to_text(b'\xff'))
        u'\xff'
        >>> show(to_text(u'\u1234'))
        u'\u1234'
        >>> show(to_text(Exception(u'\u1234')))
        u'\u1234'
        >>> show(to_text([42]))
        u'[42]'

    See source code for detailed semantics.
    """

    # Note: on py3, the `bytes` type defines an unhelpful "__str__" function,
    # so we need to do this check (see comments in ``to_bytes``).
    if not isinstance(obj, bytes):
        if isinstance(obj, text) or hasattr(obj, dundertext_name):
            return text(obj)
        obj_str = bytes(obj)
    else:
        obj_str = obj

    try:
        return text(obj_str, encoding, **decode_args)
    except UnicodeDecodeError:
        return text(obj_str, fallback, **decode_args)


class SafeFormatter(string.Formatter):
    def __init__(self, coerce_func):
        self.coerce_func = coerce_func
        string.Formatter.__init__(self)

    def format_field(self, value, format_spec):
        res = string.Formatter.format_field(self, value, format_spec)
        return self.coerce_func(res)


class MagicBytesFormatter(string.Formatter):
    def format_field(self, value, format_spec):
        value = to_text(value)
        return string.Formatter.format_field(self, value, format_spec)


safe_bytes_formatter = SafeFormatter(to_bytes)
safe_text_formatter = SafeFormatter(to_text)
magic_bytes_formatter = MagicBytesFormatter()

def _autofmthelper(name, fmt, result_type, extra, postprocess=None):
    if isinstance(fmt, types.FunctionType):
        extra = fmt.extra
        fmt = fmt.fmt

    if result_type is text:
        safe_formatter = safe_text_formatter
        fmt = text(fmt)
    elif result_type is bytes:
        safe_formatter = safe_bytes_formatter
        fmt = bytes(fmt) if PY2 else text(fmt)
    elif result_type is repr:
        safe_formatter = None
        fmt = bytes(fmt) if PY2 else text(fmt)

    def fmtfunc(self):
        kwargs = dict((k, v(self)) for (k, v) in extra.items())
        kwargs["self"] = self
        if name == "__bytes__":
            result = magic_bytes_formatter.vformat(fmt, (), kwargs)
            result = to_bytes(result)
        else:
            try:
                result = fmt.format(**kwargs)
            except UnicodeError:
                if safe_formatter is None:
                    raise
                result = safe_formatter.vformat(fmt, (), kwargs)
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
        ...     name = u"Alex \\u1234"
        ...     binary = b"\\x00\\x01\\x02"
        ...     __unicode__ = autounicode("{self.name} {self.binary}")
        ...
        >>> unicode(Person()) if PY2 else show(u'Alex \\u1234 \\x00\\x01\\x02')
        u'Alex \\u1234 \\x00\\x01\\x02'
        >>>
        """
    return _autofmthelper("__unicode__", fmt, text, kwargs)

def autostr(fmt, **kwargs):
    """ Returns a simple ``__str__`` function.
    
        On Python 2, an instance of ``str`` is returned with the same encoding
        behavior as ``autobytes`` (unicode is encoded as utf-8, bytes are left
        as bytes).

        On Python 3, an instance of ``text`` is returned with the same encoding
        behavior as ``autounicode`` (unicode is left as is, bytes are decoded
        as latin-1).

        For example::

        >>> class Person(object):
        ...     name = "Alex"
        ...     __str__ = autostr("{self.name}")
        ...
        >>> str(Person()) if PY2 else text(Person())
        'Alex'
        >>>
        """

    if isinstance(fmt, types.FunctionType):
        kwargs = fmt.extra
        fmt = fmt.fmt

    return _autofmthelper("__str__", fmt, bytes if PY2 else text, kwargs)

def autobytes(fmt, **kwargs):
    """ Returns a simple ``__bytes__`` function. Identical to ``autostr``
        on Python 2, and returns ``bytes`` on Python 3.
        
        Note: because Python 3's ``bytes`` type does not have a ``.format()``
        method we need to do a bit of magic here. Specifically, text will
        be utf-8 encoded and bytes will be left as-is.

        >>> class Person(object):
        ...     name = u"Alex \\u1234"
        ...     binary = b"\\x00\\x01\\x02"
        ...     __bytes__ = autobytes("{self.name} {self.binary}")
        ...
        >>> bytes(Person()) if PY3 else show('Alex \\xe1\\x88\\xb4 \\x00\\x01\\x02')
        b'Alex \\xe1\\x88\\xb4 \\x00\\x01\\x02'
        >>>
        """

    if isinstance(fmt, types.FunctionType):
        kwargs = fmt.extra
        fmt = fmt.fmt

    return _autofmthelper("__bytes__", fmt, bytes, kwargs)

def autorepr(fmt, **kwargs):
    """ Returns a simple ``__repr__`` function::

        >>> class Person(object):
        ...     name = "Alex"
        ...     __repr__ = autorepr(["name"])
        ...
        >>> repr(Person())
        "<autorepr.Person name='Alex' at 0x...>"
        >>> class Timestamp(object):
        ...     time = 123.456
        ...     __repr__ = autorepr(["time:0.01f"])
        ...
        >>> repr(Timestamp())
        '<autorepr.Timestamp time=123.5 at 0x...>'
        >>>
        >>> class Animal(object):
        ...     name = "Puppy"
        ...     __repr__ = autorepr(
        ...         "name={self.name!r} name_len={name_len!r}",
        ...          name_len=lambda self: len(self.name),
        ...     )
        ...
        >>> repr(Animal())
        "<autorepr.Animal name='Puppy' name_len=5 at 0x...>"
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

def autotext(text_fmt, **kwargs):
    """ Returns a triple of ``(__str__, __unicode__)`` methods,
        for simple Python 2 / Python 3 compatibility::

        >>> class Person(object):
        ...     name = "Alex"
        ...
        ...     __str__, __unicode__ = autotext("{self.name}")
        ...
        >>> show(text(Person()))
        u'Alex'
    """

    return (
        autostr(text_fmt, **kwargs),
        autounicode(text_fmt, **kwargs),
    )

if __name__ == "__main__":
    import doctest
    __name__ = "autorepr"
    doctest.testmod(optionflags=doctest.ELLIPSIS)
