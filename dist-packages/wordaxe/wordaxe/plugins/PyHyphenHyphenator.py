#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__license__="""
   Copyright 2004-2008 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''

import os.path

import hyphen as pyhyphen
import hyphen.dictools as dictools

from wordaxe.hyphen import HyphenatedWord, HyphenationPoint

from wordaxe.ExplicitHyphenator import ExplicitHyphenator

class PyHyphenHyphenator(ExplicitHyphenator):
    """
    Hyphenation using Leo's excellent pyhyphen package from 
    http://pyhyphen.googlecode.com.
    As it seems, it is triple-licensed (see its __init__.py header). 
    So it should be ok to include it here.
    To use it, you have to first download and install pyhyphen 
    using the usual python setup.py install procedure,
    then install the dictionary files you need (from OpenOffice)
    in the wordaxe/dict directory. If you have a working internet 
    connection, the dictionary file will be installed on demand.

    To use the hyphenator:

    from wordaxe.plugins.PyHyphenHyphenator import PyHyphenHyphenator
    hyphenator = PyHyphenHyphenator("de_DE",5)
    hw = hyphenator.hyphenate(u"Python-Übungsleiter")
    hw.showHyphens()
    """

    def __init__ (self, 
                  language="EN",
                  minWordLength=4,
                  quality=8,
                  hyphenDir=None,
                  **options
                 ):
        ExplicitHyphenator.__init__(self,language=language,minWordLength=minWordLength,**options)
        if hyphenDir is None:
            hyphenDir = os.path.join(os.path.split(__file__)[0], "..", "dict")
        fname = os.path.join(hyphenDir, "hyph_%s.dic" % language)
        if not dictools.is_installed(language, directory=hyphenDir):
            dictools.install(language, directory=hyphenDir)
            print "installed dictionary for %s into %s" % (language, hyphenDir)
        self.hnj = pyhyphen.hyphenator(language, directory=hyphenDir)
        self.quality = quality

    # Hilfsfunktion
    def schiebe(self,offset,L):
        return [HyphenationPoint(h.indx+offset,h.quality,h.nl,h.sl,h.nr,h.sr) for h in L]

    def zerlegeWort(self,zusgWort):
        hyphPoints = []
        for left, right in self.hnj.pairs(zusgWort):
            # Uncomment next line for an example of non-standard hyphenation
            # if left=="schif" and right=="fahrt": left="schiff"
            sl = self.shy
            if left[-1] in [u"-", self.shy]:
                sl = u""
            if left + right == zusgWort:
                hp = HyphenationPoint(len(left),self.quality,0,sl,0,u"")
            else:
                # Handle non-standard hyphenation
                # TODO: Test this.
                for i, ch in enumerate(left):
                    if ch != zusgWort[i]:
                        nl = len(left)-i
                        sl = left[i:] + sl
                        break
                else:
                    nl = 0
                    pos = len(left)
                thgir = list(right)
                thgir.reverse()
                for i, ch in enumerate(thgir):
                    if ch != zusgWort[-i-1]:
                        nr = 0
                        sr = right[:-i-1]
                        break
                else:
                    nr = 0
                    sr = right[:len(left)+len(right)-len(zusgWort)]
                    assert sr, ("This should be handled via left+right==zusgWort", left, right, zusgWort)
                hp = HyphenationPoint(len(left),self.quality,nl,sl,nr,sr)
            hyphPoints.append(hp)
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
    h = PyHyphenHyphenator("de_DE",5)
    h.add_entries({u"wordaxe":   u"word8axe",
                 })
    h.test(outfname="PyHyphenLearn.html")
    
