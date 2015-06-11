#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__license__="""
   Copyright 2004-2008 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''

import os,sys

from hyphen import *
from xml.sax.saxutils import escape,quoteattr

from wordaxe.BaseHyphenator import BaseHyphenator

VERBOSE = False

class PyHnjHyphenator(BaseHyphenator):
    """
    Hyphenation using pyHnj (Knuth's algorithm).
    @TODO  The current algorithm does NOT use Knuths algorithm,
           but a more or less trivial one.
    """

    def __init__ (self, 
                  language="EN",
                  minWordLength=4,
                  quality=8,
                  hyphenDir=None
                 ):
        BaseHyphenator.__init__(self,language=language,minWordLength=minWordLength)
        if hyphenDir is None:
            hyphenDir = os.path.join (os.path.split(__file__)[0], "dict")
        # load pattern file
        fname = os.path.join(hyphenDir,"hyph_%s.dic"%language)
        # first line is set of characters, all other lines are patterns
        # Note: we do not use a TRIE, we just store the patterns in a dict string:codes
        self.quality = quality
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
        
    # Hilfsfunktion
    def schiebe(self,offset,L):
        return [HyphenationPoint(h.indx+offset,h.quality,h.nl,h.sl,h.nr,h.sr) for h in L]

    def zerlegeWort(self,zusgWort):
        ### This was the call to pyHnj
        ### codes = self.hnj.getCodes(zusgWort.lower())
        ###
        ### Here comes the new logic.
        
        word = "." + zusgWort.lower() + "."
        #print "word=%s" % word
        # Alle Längen durchgehen (minimum: 2)
        codes = ["0"]*len(word)
        for patlen in range(2,len(word)-1):
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
        #print zusgWort
        #print "".join(codes)

        ### end of the new logic.
        
        hyphPoints = []
        for i in range(len(codes)):
            if (ord(codes[i])-ord('0')) % 2:
                hyphPoints.append(HyphenationPoint(i+1,self.quality,0,self.shy,0,u""))
        return [hyphPoints]
        
    def hyphenate(self,aWord):
        assert isinstance(aWord, unicode)
        hword = HyphenatedWord(aWord)
        loesungen = self.zerlegeWort(aWord)
        if len(loesungen)>1:
            #hword.info = ("AMBIGUOUS", loesungen)
            # nimm nur solche Trennstellen, die in allen Lösungen vorkommen,
            # und für die Qualität nimm die schlechteste.
            loesung = []
            loesung0, andere = loesungen[0], loesungen[1:]
            for i,hp in enumerate(loesung0):
                q = hp.quality
                for a in andere:
                    if q:
                        for hp1 in a:
                            if hp1.indx==hp.indx \
                            and hp1.nl==hp.nl and hp1.sl==hp.sl \
                            and hp1.nr==hp.nr and hp1.sr==hp.sr:
                                q = min(q,hp1.quality)
                                break
                        else:
                            # Trennstelle nicht in der anderen Lösung enthalten
                            q = 0
                if q:
                    loesung.append(HyphenationPoint(hp.indx,q,hp.nl,hp.sl,hp.nr,hp.sr))
        elif len(loesungen)==1:
            loesung = loesungen[0]
            #hword.info = ("HYPHEN_OK", loesung)
            if not loesung:
                pass #hword.info = ("NOT_HYPHENATABLE", aWord)
        else:
            #hword.info = ("UNKNOWN", aWord)
            loesung = []
            #for i in range(len(aWord)):
            for i in range(1,len(aWord)-1):
                if aWord[i] in self.postfixChars and aWord[i+1] not in "0123456789":
                    #print "Trenne", aWord,"an Position:",i,"bei",aWord[i]
                    # in zwei Teile zerlegen und getrennt betrachten
                    r = self.shy
                    if aWord[i] in [self.shy,u"-"]:
                       r = u""
                    loesung1 = self.hyphenate(aWord[:i])
                    loesung1.hyphenations.append (HyphenationPoint(i+1,9,0,r,0,u""))
                    loesung2 = self.hyphenate(aWord[i+1:])
                    # TODO diese Lösungen müssen jetzt zusammengeführt werden.
                    if loesung2.hyphenations == []:
                        #nur der 1. Teil kann getrennt werden
                        loesung = loesung1.hyphenations
                    else:
                        #beide Teile können getrennt werden
                        loesung = loesung1.hyphenations + [HyphenationPoint(hp.indx+i+1,hp.quality,hp.nl,hp.sl,hp.nr,hp.sr) for hp in loesung2.hyphenations]
                    break
            else:
                loesung = BaseHyphenator.hyphenate(self,aWord).hyphenations

        hword.hyphenations = loesung
        #print "hyphenate %s -> %d points" % (aWord,len(loesung))
        return hword

if __name__=="__main__":
    #print sys.stdout.encoding
    h = PyHnjHyphenator("de_DE",5)
    h.test(outfname="PyHnjLearn.html")
    