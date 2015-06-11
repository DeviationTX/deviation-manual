#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/platypus/paraparser.py
__version__=''' $Id: paraparser.py 2853 2006-05-10 12:56:39Z rgbecker $ '''

from reportlab.platypus.paraparser import *

_orig_parser = ParaParser

class ParaParser(_orig_parser):

    def setEncoding(self, enc):
        self._enc = enc
        
    def parse(self, text, style):
        
        # HVB 20070201
        if not hasattr(self, "_enc"):
            self._enc = 'cp1252' #our legacy default
        enc = self._enc
        
        return _orig_parser.parse(self, text, style)

class NoBrParaParser(ParaParser):
    """ParaParser with support for 'nobr' Tags."""

    def start_nobr( self, attributes ):
        self._push(nobr=True)

    def end_nobr( self ):
        self._pop(nobr=True)
