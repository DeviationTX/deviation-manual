#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/platypus/xpreformatted.py
__version__=''' $Id: xpreformatted.py 2426 2004-09-02 11:52:56Z rgbecker $ '''

from reportlab.platypus.xpreformatted import *

_orig_preformatted = XPreformatted

class XPreformatted(_orig_preformatted):
    def __init__(self, text, style, bulletText = None, frags=None, caseSensitive=1, dedent=0, encoding='utf8'):
        self.encoding = encoding
        _orig_preformatted.__init__(self, text, style, bulletText, frags, caseSensitive, dedent)

if __name__=='__main__':    #NORUNTESTS
    def dumpXPreformattedLines(P):
        print '\n############dumpXPreforemattedLines(%s)' % str(P)
        lines = P.blPara.lines
        n =len(lines)
        for l in range(n):
            line = lines[l]
            words = line.words
            nwords = len(words)
            print 'line%d: %d(%d)\n  ' % (l,nwords,line.wordCount),
            for w in range(nwords):
                print "%d:'%s'"%(w,words[w].text),
            print

    def dumpXPreformattedFrags(P):
        print '\n############dumpXPreforemattedFrags(%s)' % str(P)
        frags = P.frags
        n =len(frags)
        for l in range(n):
            print "frag%d: '%s'" % (l, frags[l].text)

        l = 0
        for L in _getFragLines(frags):
            n=0
            for W in _getFragWords(L):
                print "frag%d.%d: size=%d" % (l, n, W[0]),
                n = n + 1
                for w in W[1:]:
                    print "'%s'" % w[1],
                print
            l = l + 1

    def try_it(text,style,dedent,aW,aH):
        P=XPreformatted(text,style,dedent=dedent)
        dumpXPreformattedFrags(P)
        w,h = P.wrap(aW, aH)
        dumpXPreformattedLines(P)
        S = P.split(aW,aH)
        dumpXPreformattedLines(P)
        for s in S:
            s.wrap(aW,aH)
            dumpXPreformattedLines(s)
            aH = 500

    from wordaxe.rl.styles import getSampleStyleSheet, ParagraphStyle
    styleSheet = getSampleStyleSheet()
    B = styleSheet['BodyText']
    DTstyle = ParagraphStyle("discussiontext", parent=B)
    DTstyle.fontName= 'Helvetica'
    for (text,dedent,style, aW, aH, active) in [('''


The <font name=courier color=green>CMYK</font> or subtractive

method follows the way a printer
mixes three pigments (cyan, magenta, and yellow) to form colors.
Because mixing chemicals is more difficult than combining light there
is a fourth parameter for darkness.  For example a chemical
combination of the <font name=courier color=green>CMY</font> pigments generally never makes a perfect

black -- instead producing a muddy color -- so, to get black printers
don't use the <font name=courier color=green>CMY</font> pigments but use a direct black ink.  Because
<font name=courier color=green>CMYK</font> maps more directly to the way printer hardware works it may
be the case that &amp;| &amp; | colors specified in <font name=courier color=green>CMYK</font> will provide better fidelity
and better control when printed.


''',0,DTstyle, 456.0, 42.8, 0),
('''

   This is a non rearranging form of the <b>Paragraph</b> class;
   <b><font color=red>XML</font></b> tags are allowed in <i>text</i> and have the same

      meanings as for the <b>Paragraph</b> class.
   As for <b>Preformatted</b>, if dedent is non zero <font color=red size=+1>dedent</font>
       common leading spaces will be removed from the
   front of each line.

''',3, DTstyle, 456.0, 42.8, 0),
("""\
    <font color=blue>class </font><font color=red>FastXMLParser</font>:
        # Nonsense method
        def nonsense(self):
            self.foo = 'bar'
""",0, styleSheet['Code'], 456.0, 4.8, 1),
]:
        if active: try_it(text,style,dedent,aW,aH)
