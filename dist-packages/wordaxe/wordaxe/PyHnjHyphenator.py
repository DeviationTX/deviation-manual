#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__license__="""
   Copyright 2004-2008 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''

import os,sys
import copy

from wordaxe.hyphen import *
from xml.sax.saxutils import escape,quoteattr

from wordaxe.ExplicitHyphenator import ExplicitHyphenator

VERBOSE = False

class PyHnjHyphenator(ExplicitHyphenator):
    """
    Hyphenation using pyHnj (Knuth's algorithm).
    The pyHnj/libhnj code does not work if german words contain umlauts.
    As a work-around you can use a pure python version that does
    not use pyHnj/libhnj and should give the same results.
    """

    def __init__ (self, 
                  language="EN",
                  minWordLength=4,
                  quality=8,
                  hyphenDir=None,
                  purePython=False,
                  **options
                 ):
        """ Note:
            The purePython version does NOT use Knuth's algorithm,
            but a more simple (and slower) algorithm.
        """
        ExplicitHyphenator.__init__(self,language=language,minWordLength=minWordLength, **options)
        if hyphenDir is None:
            hyphenDir = os.path.join(os.path.split(__file__)[0], "dict")
        self.purePython = purePython
        fname = os.path.join(hyphenDir, "hyph_%s.dic" % language)
        # first line is set of characters, all other lines are patterns
        if self.purePython:
            # Note: we do not use a TRIE, we just store the patterns in a dict string:codes
            lines = open(fname).read().splitlines()
            self.characters = lines.pop(0)
            self.patterns = {}
            for pattern in lines:
                pat = ""
                codes = ""
                digit = "0"
                for ch in pattern:
                    if ch>='0' and ch<='9':
                        digit = ch
                    else:
                        codes = codes+digit
                        pat = pat+ch
                        digit = "0"
                codes = codes+digit
                self.patterns[pat.decode("iso-8859-1")] = codes
        else:
            import pyHnj
            self.hnj = pyHnj.Hyphen(fname)
        self.quality = quality

    # Hilfsfunktion
    def schiebe(self,offset,L):
        return [HyphenationPoint(h.indx+offset,h.quality,h.nl,h.sl,h.nr,h.sr) for h in L]

    def zerlegeWort(self,zusgWort):
        if self.purePython:
            word = "." + zusgWort.lower() + "."
            # Alle Längen durchgehen (minimum: 2)
            codes = ["0"]*len(word)
            for patlen in range(2,len(word)):
                #print "patlen %d" % patlen
                for startindx in range(len(word)-patlen):
                    #print "startindx %d" % startindx
                    try:
                        patcode = self.patterns[word[startindx:startindx+patlen]]
                        #print "testpat=%s patcode=%s" % (word[startindx:startindx+patlen],patcode)
                        for i,digit in enumerate(patcode):
                            if digit > codes[i+startindx]:
                                codes[i+startindx] = digit
                    except KeyError:
                        pass
            codes = codes[2:-1]
        else:
            codes = self.hnj.getCodes(zusgWort.lower())
        hyphPoints = []
        for i, code in enumerate(codes):
            # wir trennen nicht das erste oder letzte Zeichen ab
            if i==0 or i==len(codes)-1:
                continue
            if (ord(code)-ord('0')) % 2:
                hyphPoints.append(HyphenationPoint(i+1,self.quality,0,self.shy,0,""))
        return hyphPoints
        
    def hyph(self,aWord):
        assert isinstance(aWord, unicode)
        hword = HyphenatedWord(aWord, hyphenations=self.zerlegeWort(aWord))
        # None (unknown) kann hier nicht vorkommen, da der
        # Algorithmus musterbasiert funktioniert und die Wörter
        # sowieso nicht "kennt" oder "nicht kennt".
        return hword

    def i_hyphenate(self, aWord):
        return ExplicitHyphenator.i_hyphenate_derived(self, aWord)
    
if __name__=="__main__":
    h = PyHnjHyphenator("de_DE",5, purePython=True)
    h.test(outfname="PyHnjLearn.html")
    
