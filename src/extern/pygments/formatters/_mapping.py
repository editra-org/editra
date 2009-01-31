# -*- coding: utf-8 -*-
"""
    pygments.formatters._mapping
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Formatter mapping defintions. This file is generated by itself. Everytime
    you change something on a builtin formatter defintion, run this script from
    the formatters folder to update it.

    Do not alter the FORMATTERS dictionary by hand.

    :copyright: 2006-2007 by Armin Ronacher, Georg Brandl.
    :license: BSD, see LICENSE for more details.
"""

from pygments.util import docstring_headline

# start
from pygments.formatters.bbcode import BBCodeFormatter
from pygments.formatters.html import HtmlFormatter
from pygments.formatters.img import BmpImageFormatter
from pygments.formatters.img import GifImageFormatter
from pygments.formatters.img import ImageFormatter
from pygments.formatters.img import JpgImageFormatter
from pygments.formatters.latex import LatexFormatter
from pygments.formatters.other import NullFormatter
from pygments.formatters.other import RawTokenFormatter
from pygments.formatters.rtf import RtfFormatter
from pygments.formatters.svg import SvgFormatter
from pygments.formatters.terminal import TerminalFormatter
from pygments.formatters.terminal256 import Terminal256Formatter

FORMATTERS = {
    BBCodeFormatter: ('BBCode', ('bbcode', 'bb'), (), 'Format tokens with BBcodes. These formatting codes are used by many bulletin boards, so you can highlight your sourcecode with pygments before posting it there.'),
    BmpImageFormatter: ('img_bmp', ('bmp', 'bitmap'), ('*.bmp',), 'Create a bitmap image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'),
    GifImageFormatter: ('img_gif', ('gif',), ('*.gif',), 'Create a GIF image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'),
    HtmlFormatter: ('HTML', ('html',), ('*.html', '*.htm'), "Format tokens as HTML 4 ``<span>`` tags within a ``<pre>`` tag, wrapped in a ``<div>`` tag. The ``<div>``'s CSS class can be set by the `cssclass` option."),
    ImageFormatter: ('img', ('img', 'IMG', 'png'), ('*.png',), 'Create a PNG image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'),
    JpgImageFormatter: ('img_jpg', ('jpg', 'jpeg'), ('*.jpg',), 'Create a JPEG image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'),
    LatexFormatter: ('LaTeX', ('latex', 'tex'), ('*.tex',), 'Format tokens as LaTeX code. This needs the `fancyvrb` and `color` standard packages.'),
    NullFormatter: ('Text only', ('text', 'null'), ('*.txt',), 'Output the text unchanged without any formatting.'),
    RawTokenFormatter: ('Raw tokens', ('raw', 'tokens'), ('*.raw',), 'Format tokens as a raw representation for storing token streams.'),
    RtfFormatter: ('RTF', ('rtf',), ('*.rtf',), 'Format tokens as RTF markup. This formatter automatically outputs full RTF documents with color information and other useful stuff. Perfect for Copy and Paste into Microsoft\xc2\xae Word\xc2\xae documents.'),
    SvgFormatter: ('SVG', ('svg',), ('*.svg',), 'Format tokens as an SVG graphics file.  This formatter is still experimental. Each line of code is a ``<text>`` element with explicit ``x`` and ``y`` coordinates containing ``<tspan>`` elements with the individual token styles.'),
    Terminal256Formatter: ('Terminal256', ('terminal256', 'console256', '256'), (), 'Format tokens with ANSI color sequences, for output in a 256-color terminal or console. Like in `TerminalFormatter` color sequences are terminated at newlines, so that paging the output works correctly.'),
    TerminalFormatter: ('Terminal', ('terminal', 'console'), (), 'Format tokens with ANSI color sequences, for output in a text console. Color sequences are terminated at newlines, so that paging the output works correctly.')
}

if __name__ == '__main__':
    import sys
    import os

    # lookup formatters
    found_formatters = []
    imports = []
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    for filename in os.listdir('.'):
        if filename.endswith('.py') and not filename.startswith('_'):
            module_name = 'pygments.formatters.%s' % filename[:-3]
            print module_name
            module = __import__(module_name, None, None, [''])
            for formatter_name in module.__all__:
                imports.append((module_name, formatter_name))
                formatter = getattr(module, formatter_name)
                found_formatters.append(
                    '%s: %r' % (formatter_name,
                                (formatter.name,
                                 tuple(formatter.aliases),
                                 tuple(formatter.filenames),
                                 docstring_headline(formatter))))
    # sort them, that should make the diff files for svn smaller
    found_formatters.sort()
    imports.sort()

    # extract useful sourcecode from this file
    f = open(__file__)
    try:
        content = f.read()
    finally:
        f.close()
    header = content[:content.find('# start')]
    footer = content[content.find("if __name__ == '__main__':"):]

    # write new file
    f = open(__file__, 'w')
    f.write(header)
    f.write('# start\n')
    f.write('\n'.join(['from %s import %s' % imp for imp in imports]))
    f.write('\n\n')
    f.write('FORMATTERS = {\n    %s\n}\n\n' % ',\n    '.join(found_formatters))
    f.write(footer)
    f.close()
