'''
Registers a special handler for named HTML entities

Usage:
import named_entities
text = u'Some string with Unicode characters'
text = text.encode('ascii', 'named_entities')
'''

import codecs
from htmlentitydefs import codepoint2name

def named_entities(text):
    if isinstance(text, (UnicodeEncodeError, UnicodeTranslateError)):
        s = []
        for c in text.object[text.start:text.end]:
            if ord(c) in codepoint2name:
                s.append(u'&%s;' % codepoint2name[ord(c)])
            else:
                s.append(u'&#%s;' % ord(c))
        return ''.join(s), text.end
    else:
        raise TypeError("Can't handle %s" % text.__name__)
codecs.register_error('named_entities', named_entities)