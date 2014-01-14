"""Python 2/3 compatibility symbols.

isinstance() checks:
 * Use string_types instead of 2's basestring
 * Use int_types instead of 3's int

sha1:
 * Silently accepts unicode so long as it's ASCII

quote_str:
 * Version of 2's repr() that won't add a 'u' prefix (different versions of
   Python put it or not)

StringIO
"""

from abc import ABCMeta
import hashlib


try:
    string_types = basestring
except NameError:
    string_types = str

try:
    long
except NameError:
    int_types = int
else:
    class int_types:
        __metaclass__ = ABCMeta
    int_types.register(int)
    int_types.register(long)


class sha1(object):
    def __init__(self, arg=b''):
        self._hash = hashlib.sha1()
        if arg:
            self.update(arg)

    def update(self, arg):
        if not isinstance(arg, bytes):
            arg = arg.encode('ascii')
        self._hash.update(arg)

    def hexdigest(self):
        return self._hash.hexdigest()


if bytes == str:
    unicode_type = unicode
else:
    unicode_type = str


def quote_str(s):
    return "'%s'" % s.replace("\\", "\\\\").replace('"', '\\"')


try:
    # CPython 2
    from cStringIO import StringIO
except ImportError:
    try:
        # Python 2
        from StringIO import StringIO
    except ImportError:
        # Python 3
        from io import StringIO
