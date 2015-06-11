#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

__license__="""
   Copyright 2004-2008 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''

import codecs

from wordaxe.hyphen import SHY, HyphenatedWord
from wordaxe.BaseHyphenator import BaseHyphenator
from wordaxe.hyphrules import decodeTrennung

class ExplicitHyphenator(BaseHyphenator):
    """
    Allow to explicitly specify how a word should be hyphenated.
    This is a slight improvement compared to BaseHyphenator.
    
    Usage:
    
    hyphenator = ExplicitHyphenator("DE")
    # Add explicit hyphenation for a single word.
    hyphenator.add_entry(u"analphabet", u"an8alpha5bet")
    # Add several entries
    hyphenator.add_entries({u"urinstinkt":   u"ur8instinkt",
                            u"urinstinkte":  u"ur8instinkte",
                            u"urinstinkten": u"ur8instinkt3en",
                           })
    
    The last entry is probably not correctly hyphenated
    according to the german hyphenation rules, but you don't
    want to read "urinstink" in a text...
    
    The add_entry/add_entries usually expect unicode strings.
    Bytes strings require the encoding argument to be supplied.
    hyphenator.add-entries ("bräutigam", "bräu5ti5gam", encoding="iso-8859").
    
    Instead of using numbers for defining the quality of a hyphenation
    point, you may use the "~" (tilde) character, corresponding to
    a medium quality hyphenation point: "bräu~ti~gam".
    """

    def __init__ (self, 
                  language="DE",
                  minWordLength=4,
                  qHaupt=8,
                  qNeben=5,
                  qVorsilbe=5,
                  qSchlecht=3,
                  hyphenDir=None,
                  **options
                 ):
        BaseHyphenator.__init__(self,language=language,minWordLength=minWordLength,**options)

        # Qualitäten für verschiedene Trennstellen
        self.qHaupt=qHaupt
        self.qNeben=qNeben
        self.qVorsilbe=qVorsilbe
        self.qSchlecht=qSchlecht
        
        # Stammdaten initialisieren
        self.sonderfaelle = []
        
    def add_entry(self, word, trennung, encoding=unicode):
        if not isinstance(word, unicode):
            word = unicode(word, encoding)
        if not isinstance(trennung, unicode):
            trennung = unicode(trennung, encoding)
        # Ignore Case @TODO Umlaute usw.!
        word = word.lower() 
        trennung = trennung.replace(u"~", u"5")
        lenword = len(word)
        for (lae, L) in self.sonderfaelle:
            if lae == lenword:
                L[word] = trennung
                break
        else:
            self.sonderfaelle.append((lenword,{word: trennung}))
            
    def add_entries(self, mapping, encoding=unicode):
        for word, trennung in mapping.items():
            self.add_entry(word, trennung, encoding)
            
    def add_entries_from_file(self, filename, encoding=None):
        """
        Add entries from a text file (interpreting the file
        using the given encoding). If encoding is not given
        or None, try to extract the encoding from a line
        near the start of the file like
        # -*- coding: iso-8859-1 -*-
        """
        if encoding is None:
            import re
            frag = open(filename,"rt").read(1000)
            m = re.search(r"-\*- coding: ([^ ]+) -\*-", frag)
            if m is not None:
                encoding = m.group(1)
            else:
                raise ValueError("Encoding not specified and not found in file")
        fh = codecs.open(filename, "rt", encoding)
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            word, trennung = line.split()
            self.add_entry(word, trennung)
        fh.close()
        
        
    def hyph(self, word):
        #print "ExplicitHyphenator hyph", word
        lenword = len(word)
        for (lae, L) in self.sonderfaelle:
            if lae == lenword:
                trennung = L.get(word.lower(), None)
                if trennung is not None:
                    hword = HyphenatedWord(word, decodeTrennung(trennung))
                    return hword
                break
        # Wort nicht gefunden
        return None
        
    def i_hyphenate(self, aWord):
        assert isinstance(aWord, unicode)
        return self.stripper.apply_stripped(ExplicitHyphenator.hyph, self, aWord)

    def i_hyphenate_derived(self,aWord):
        """
        You can use this method in classes derived from ExplicitHyphenator.
        It will first split the word using BaseHyphenator,
        then for each "subword" it will call ExplicitHyphenator,
        and only call the derived classes hyph method for the still
        unknown subwords.
        
        TODO: The implementation does not match the docstring
              test: "hohenlimburg.de", "hohenlimburg.de)"
        """
        #print "ExplicitHyphenator.i_hyphenate_derived", aWord
        assert isinstance(aWord, unicode)

        # Helper function
        
        sub_hwords = []
        hword = BaseHyphenator.i_hyphenate(self,aWord)
        #print "BaseHyphenator.i_hyphenate returned %r" % hword
        if hword is None:
            hword = HyphenatedWord(aWord,hyphenations=[])
        base_hyph_points = hword.hyphenations
        last_indx = 0
        nr = 0
        for hpnum, hp in enumerate(base_hyph_points):
            if isinstance(hp, int):
                hp = HyphenationPoint(hp, quality=5, sl=SHY)
            subword = hword[last_indx+nr:hp.indx]
            # handle subword
            if SHY in subword:
                sub_hword = self.stripper.apply_stripped(BaseHyphenator.hyph, self, subword)
            else:
                sub_hword = self.stripper.apply_stripped(ExplicitHyphenator.hyph, self, subword)
            if sub_hword is None:
                sub_hword = self.stripper.apply_stripped(self.hyph, self, subword)
            if sub_hword is None:
                sub_hword = HyphenatedWord(subword, hyphenations=[])
            sub_hwords.append(sub_hword)
            # end handle subword
            last_indx = hp.indx
            nr = hp.nr            
        # Now the last subword
        subword = hword[last_indx:]
        # handle subword
        if SHY in subword:
            sub_hword = self.stripper.apply_stripped(BaseHyphenator.hyph, self, subword)
        else:
            sub_hword = self.stripper.apply_stripped(ExplicitHyphenator.hyph, self, subword)
        if sub_hword is None:
            sub_hword = self.stripper.apply_stripped(self.hyph, self, subword)
        if sub_hword is None:
            sub_hword = HyphenatedWord(subword, hyphenations=[])
        sub_hwords.append(sub_hword)
        #end handle subword
        if len(sub_hwords) > 1:
            return HyphenatedWord.join(sub_hwords)
        else:        
            return sub_hwords[0] # Kann auch None sein.


if __name__=="__main__":
    h = ExplicitHyphenator("DE",5)
    h.add_entry("Bräutigam", "Bräu5ti5gam", "iso-8859-1")
    h.add_entries({u"Urinstinkt": u"Ur8instinkt",
                   u"Urinstinkte": u"Ur8instinkte",
                   u"Urinstinkten": u"Ur8instinkt3en",
                  }
                 )
    h.test(outfname="ExplicitLearn.html")
