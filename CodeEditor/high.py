from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def format(color, style=''):
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'keyword': format('#ff5500'),
    'operator': format('red'),
    'brace': format('#d5ff00'),
    'defclass': format('#ffbf00', 'bold'),
    'string': format('#ABFF79'),
    'string2': format('#ffbf00'),
    'comment': format('#ff4141', 'italic'),
    'self': format('#aa00ff', 'italic'),
    'numbers': format('#47c5ff'),
}

class PythonHighlighter (QSyntaxHighlighter):
    python_keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False', 'using', 'main',
    ]

    c_keywords = [
        'auto', 'break', 'case', 'char',
        'const', 'continue', 'default', 'do',
        'double', 'else', 'enum', 'extern',
        'float', 'for', 'goto', 'if',
        'int', 'long', 'register', 'return',
        'short', 'signed', 'sizeof', 'static',
        'struct', 'switch', 'typedef', 'union',
        'unsigned', 'void', 'volatile', 'while'
    ]


    operators = [
        '=',

        '==', '!=', '<', '<=', '>', '>=',

        '\+', '-', '\*', '/', '//', '\%', '\*\*',

        '\+=', '-=', '\*=', '/=', '\%=',

        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document, is_python=True):
        QSyntaxHighlighter.__init__(self, document)

        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        keywords = PythonHighlighter.python_keywords if is_python \
            else PythonHighlighter.c_keywords
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        rules += [
            (r'\bself\b', 0, STYLES['self']),

            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),

            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),

            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            (r'#[^\n]*', 0, STYLES['comment']),

            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]
        if not is_python:
            rules.append((r'//[^\n]*', 0, STYLES['comment']),)

        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter.indexIn(text)
            add = delimiter.matchedLength()

        while start >= 0:
            end = delimiter.indexIn(text, start + add)

            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add

            self.setFormat(start, length, style)

            start = delimiter.indexIn(text, start + length)

        if self.currentBlockState() == in_state:
            return True
        else:
            return False

