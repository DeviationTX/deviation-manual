#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__license__="""
   Copyright 2004-2008 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''

import os,sys
import copy
import operator
import codecs

from wordaxe.hyphen import SHY,HyphenationPoint,HyphenatedWord
import time
from wordaxe.BaseHyphenator import Stripper, BaseHyphenator
from wordaxe.ExplicitHyphenator import ExplicitHyphenator

from wordaxe.hyphrules import HyphRule, RULES, AlgorithmError

from wordaxe.hyphrules import NO_CHECKS,StringWithProps,Prefix,Root,Suffix
from wordaxe.hyphrules import TRENNUNG,NO_SUFFIX,KEEP_TOGETHER
import wordaxe.dict.DEhyph as DEhyph

DEBUG=0

import logging
logging.basicConfig()
log = logging.getLogger("DCW")
log.setLevel(logging.INFO)
if DEBUG:
    log.setLevel(logging.DEBUG)

class WordFrag:
    """Helper class for a (partially) parsed WordFrag.
       A WordFrag is made up from prefix_chars, prefix, root, suffix, and suffix_chars,
       i.e. the german word "(unveränderbarkeit)!" 
       is a WordFrag ( "(", ["un","ver"], "änder", ["bar","keit"], ")!" ).
    """
       
    def __init__(self,konsonantenverkuerzung_3_2=False):
        self.konsonantenverkuerzung_3_2 = konsonantenverkuerzung_3_2
        self.prefix_chars = ""
        self.prefix = []
        self.root = None
        self.suffix = None
        self.suffix_chars = ""
        self.checks = [[],[],[],[],[],[]]

    def isValid(self):
       "Is the WordFrag (stand alone) a valid word?"
       return False
       
    def __str__(self):
       "String representation"
       return self.__class__.__name__
       
    def __repr__(self):
       return self.__str__()
    
    def clone(self):
        return copy.copy(self)

class PrefixWordFrag(WordFrag):
    """A WordFrag that does not yet contain the root.
    """
    def __init__(self,tw,prefix_chars="",prefix=[]):
        if tw is None: tw = WordFrag()
        # Auch alle sonstigen Attribute der Vorlage mit übernehmen
        # @TODO Dieser Code ist wirklich hässlich:
        self.__dict__.update(tw.__dict__)
        WordFrag.__init__(self,konsonantenverkuerzung_3_2=tw.konsonantenverkuerzung_3_2)
        self.prefix_chars = prefix_chars or tw.prefix_chars
        self.prefix = prefix or tw.prefix

    def __str__(self):
       "String representation"
       return "PrefixWF " + self.prefix_chars + "-".join([p.strval for p in self.prefix])

    def clone(self):
        n = copy.copy(self)
        n.prefix = self.prefix[:]
        return n
        
class SuffixWordFrag(PrefixWordFrag):
    """A WordFrag that does contain a root and eventually a suffix.
    """
    def __init__(self,tw,root=None,suffix=[],suffix_chars=[]):
        if tw is None: tw = PrefixWordFrag(None,[])
        PrefixWordFrag.__init__(self,tw)
        self.root = root or tw.root
        self.suffix = suffix
        self.suffix_chars = suffix_chars

    def __str__(self):
       "String representation"
       return "SuffixWF " + self.prefix_chars + "-".join([p.strval for p in self.prefix]) + \
              "|" + self.root.strval + "|" + ":".join([s.strval for s in self.suffix]) + \
              (self.konsonantenverkuerzung_3_2 and "!3>2" or "")

    def clone(self):
        n = copy.copy(self)
        n.suffix = self.suffix[:]
        
        return n

    def isValid(self):    
        if not self.suffix:
            for p in self.root.props:
                if isinstance (p,NEED_SUFFIX):
                    return False
        return True
        
SWORD = SuffixWordFrag

VOWELS = u"aeiouäöüy"

ALTE_REGELN = False

KONSTANTEN_VERKUERZUNG_3_2 = True

VERBOSE = False

GENHTML = False

class DCWHyphenator(ExplicitHyphenator):
    """
    Hyphenation by decomposition of composed words.
    The German language has a lot of long words that are
    composed of simple words. The German word
    "Silbentrennung" (engl. hyphenation) is a good example
    in itself.
    It is a composition of the words "Silbe" (engl. syllable)
    and "Trennung" (engl. "separation").
    Each simple word consists of 0 or more prefixes, 1 stem,
    and 0 or more suffixes.
    The principle of the algorithm is quite simple.
    It uses a a base of known prefixes, stems and suffixes,
    each of which may contain attributes that work as rules.
    The rules define how these word fragments can be combined.
    The algorithm then to decompose the whole word into a
    series of simple words, where each simple word consists
    of known fragments and fulfills the rules.
    Then it uses another simple algorithm to hyphenate each
    simple word.
    For a given word, there may be more than one possible
    decomposition into simple words.
    The hyphenator only returns those hyphenation points that
    ALL possible decompositions have in common.
    
    Note:
    The algorithm has been inspired by the publications about
    "Sichere sinnentsprechende Silbentrennung" from the 
    technical university of Vienna, Austria (TU Wien).
    However, it is in no other way related to the closed-source
    software "SiSiSi" software developed at the TU Wien.
    For more information about the "SiSiSi" software, see the
    web site "http://www.ads.tuwien.ac.at/research/SiSiSi/".
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
        ExplicitHyphenator.__init__(self,language=language,minWordLength=minWordLength, **options)

        # Qualitäten für verschiedene Trennstellen
        self.qHaupt=qHaupt
        self.qNeben=qNeben
        self.qVorsilbe=qVorsilbe
        self.qSchlecht=qSchlecht
        
        # Stammdaten initialisieren
        special_words = []
        self.roots = []
        self.prefixes = []
        self.suffixes = []
        self.prefix_chars = DEhyph.prefix_chars
        self.suffix_chars = DEhyph.suffix_chars
        self.maxLevel=20
        
        # Statistikdaten initialisieren
        self.numStatesExamined = 0
        
        # [special_words] einlesen
        for zeile in DEhyph.special_words.splitlines():
            # Leerzeilen und Kommentare überspringen
            zeile = zeile.strip()
            if not zeile or zeile.startswith("#"):
                continue
            if "=" in zeile:
                word, trennung = zeile.split("=")
            else:
                zeile = zeile.split(",")
                word = zeile.pop(0)
                assert len(zeile) >= 1
                for attr in zeile:
                    if ":" in attr:
                        propnam, propval = attr.split(":")
                    else:
                        propnam, propval = attr, ""
                    if propnam == u"TRENNUNG":
                        trennung = propval
                    elif propnam == u"KEEP_TOGETHER":
                        trennung = word
                    else:
                        raise NameError("Unknown property for word %s: %s" % (word, propnam))
                        pass # Attribut ignorieren
            self.add_entry(word, trennung)

        
        # roots, prefixes und suffixes einlesen.
        # Bei diesen können noch - Komma-getrennt - Eigenschaften angegeben sein.
        # Eine Eigenschaft hat die Form XXX oder XXX:a,b,c
        for name in ["roots", "prefixes", "suffixes"]:
            abschnitt = getattr(self, name)
            zeilen = getattr(DEhyph, name)
            assert isinstance(zeilen, unicode)
            for zeile in zeilen.splitlines():
                # Leerzeilen und Kommentare überspringen
                zeile = zeile.strip()
                if not zeile or zeile.startswith("#"):
                    continue
                # Aufteilen in word und props
                zeile = zeile.split(",")
                word = zeile.pop(0)
                props = []
                if len(zeile) >= 1:
                  for attr in zeile:
                    if ":" in attr:
                        [propnam,propval] = attr.split(":")
                    else:
                        propnam = attr
                        propval = ""
                    try:
                        cls = RULES[propnam]
                        props.append(cls(propval)) # the class is the propnam
                    except KeyError:
                        raise NameError("Unknown property for word %s: %s" % (word,propnam))
                # Jeder abschnitt ist eine Liste von Tupeln (lae, L), wobei L
                # ein Dictionary von Wörtern der Länge lae ist und dazu die Liste
                # der möglichen Eigenschaften enthält (dasselbe Wort kann je nach 
                # Bedeutung unterschiedliche Eigenschaften haben).
                lenword = len(word)
                for (lae,L) in abschnitt:
                    if lae==lenword:
                      try:
                          L[word].append(props)
                      except KeyError:
                          L[word]=[props]
                      break
                else:
                    abschnitt.append((lenword,{word:[props]}))
        self.stripper = Stripper(self.prefix_chars, self.suffix_chars)

    def _zerlegeWort(self,zusgWort):
        """"
        Returns a list containing all possible decompositions.
        The decomposition routine works as follows:

        A TODO list contains the cases that still have to be considered.
        Each element in this list is a tuple
        (cword,frag,remainder,checks) characterising the state precisely.
        
        Notation:
        CWORD = compound word, a list of SWORDs
        SWORD = simple word = prefix* root suffix*

        cword is a list containing the already parsed SWORDs.
        frag is a fragment of the current SWORD.
        remainder is the remainder of the unparsed words.
        checks describes the checks we still have to do.
        
        A solution list contains the solutions found so far
        (it is empty in the beginning).
        
        In the beginning, the TODO-list contains only one element,
        the initial status:
        ([], None, zusgWort, [])
        
        For the word "Wegbeschreibung", a status could
        look like this:
        ( [ SWORD([],Root("Weg"),[]) ],
          SuffixWordFrag ([Prefix("be")],Root("schreib"),[]),
          "ung",
          []
        )
        
        If the TODO list is empty, the solutions found are returned.
        
        Otherwise, one element of the list is removed and examined.
        Depending on the frag, we try all possible extensions of the
        frag with a prefix,root or postfix.
        If a continuation is possible, then the continued frag
        and is appended to the TODO list.
        """

        def mergeChecks(c1,c2):
            """Create a new list of checks from c1 and c2
            """
            return map(operator.__add__,c1,c2)
        
        def do_check_frag(when,cword,frag,checks):
            """Run the PRE_WORD or PRE_NEXT_WORD checks before appending frag to cword.
            """
            for chk in checks[when]:
              try:
                if not chk.check(cword,when,frag):
                    #log.debug ("check (chk=%r, when=%d) failed for frag %r", chk, when, frag)
                    return False
              except AlgorithmError:
                log.error ("check %s when=%d : AlgorithmError for cword=%r, frag=%r", chk, when, cword, frag)
                return False
            return True
        
        def do_check_piece(when,frag,piece,checks):
            """Run the PRE_PIECE or PRE_NEXT_PIECE checks before appending piece to frag.
            """
            for chk in checks[when]:
                if not chk.check(frag,when,piece):
                    log.debug ("check (chk=%r, when=%d) failed for piece %r", chk, when, piece.strval)
                    return False
            return True
        
        def check_PRE_WORD(cword,frag,checks):
            return do_check_frag(HyphRule.PRE_WORD,cword,frag,checks)

        def check_PRE_NEXT_WORD(cword,frag,checks):
            return do_check_frag(HyphRule.PRE_NEXT_WORD,cword,frag,checks)

        def check_AT_END(cword,checks):
            return do_check_frag(HyphRule.AT_END,cword,None,checks)
        
        def check_PRE_PIECE(frag,piece,checks):
            return do_check_piece(HyphRule.PRE_PIECE,frag,piece,checks)

        def check_PRE_NEXT_PIECE(frag,piece,checks):
            return do_check_piece(HyphRule.PRE_NEXT_PIECE,frag,piece,checks)

        def check_PRE_ROOT(frag,piece,checks):
            return do_check_piece(HyphRule.PRE_ROOT,frag,piece,checks)

        # Initialization
        solutions = []
        todo = []
        state = ( [], None, zusgWort, NO_CHECKS())
        todo.append (state)
        
        while todo:

            #log.debug ("todo=\n%r", todo)
            
            # Consider the next state
            state = todo.pop()
            (cword,frag,remainder,checks) = state
            
            log.debug ("Examining state: %r", state)
            self.numStatesExamined += 1
            
            # check if the SWORD can end here
            if frag and frag.root \
            and check_PRE_WORD(cword,frag,checks) \
            and check_PRE_NEXT_WORD(cword,frag,checks):
                #### log.warn ("@TODO: The above IF statement is DEFINITELY wrong - frag: %r", frag)
                #### Ich bin mir da nicht mehr so sicher, es scheint doch richtig zu sein.

                #log.debug ("Since fragment has a root, add test with None.")
                newChecks = NO_CHECKS()
                newChecks[HyphRule.AT_END] = checks[HyphRule.AT_END]
                todo.append( (cword+[frag],None,remainder,newChecks) )
            
            if remainder=="":  # we have reached the end of the word.

                if frag is None:  # good, we have no incomplete fragment
                
                    if check_AT_END(cword,checks): # the last checks are ok
                        log.debug ("found solution: %r", cword)
                        solutions.append(cword)
                    else:
                        pass
                        log.debug ("check_AT_END failed for %r", cword)
                        
                else: # we have a fragment of an SWORD.
                    pass
                    #log.debug ("Incomplete or invalid sword fragment found at end of string.\n" +
                    #    "We should already have added the case where fragment is None\n" +
                    #    "to our todo list, so we just can skip this case: %r", frag)

                        
            else:  # still more characters to parse
            
                if frag is None: 
                
                    log.debug ("frag is None, remainder=%r bei zerlegeWort %r", remainder, zusgWort)
                
                    # check prefix characters
                    l = 0
                    while l<len(remainder) and remainder[l] in self.prefix_chars:
                        l = l+1
                    if l>0:
                        ###HVB, 14.10.2006 geändert
                        ###newfrag = frag.clone()
                        ###newfrag.prefix_chars = remainder[:l]
                        ###r = remainder[l:]
                        ###todo.append ( (cword,newfrag,r,checks) )
                        ###continue # do not examine the current state any more.
                        newfrag = PrefixWordFrag(None, prefix_chars=remainder[:l])
                        r = remainder[l:]
                        todo.append ( (cword,newfrag,r,checks) )
                        continue # do not examine the current state any more.
                    else:
                        # we need a fragment (even if it is empty) from here on.
                        frag = PrefixWordFrag(None)
                
                if not frag.root: # fragment has not yet a root.

                    # check all possible prefixes.
                    #log.debug ("checking prefixes.")
                    for (lae,L) in self.prefixes:
                      l,r = remainder[:lae],remainder[lae:]
                      for eigenschaften in L.get(l,[]):
                          #log.debug ("trying prefix: %s with properties: %s", l,eigenschaften)
                          piece = Prefix(l,eigenschaften)
                          pChecks = piece.getChecks()
                          if check_PRE_PIECE(frag,piece,pChecks):
                              if check_PRE_NEXT_PIECE(frag,piece,checks):
                                  # @TODO perhaps the next few lines could be faster and more elegant
                                  newChecks = mergeChecks(checks,pChecks)
                                  newChecks[HyphRule.PRE_PIECE] = []
                                  newChecks[HyphRule.PRE_NEXT_PIECE] = pChecks[HyphRule.PRE_NEXT_PIECE]
                                  newfrag = copy.copy(frag)
                                  newfrag.prefix = frag.prefix + [piece]
                                  todo.append( (cword,newfrag,r,newChecks) )
                              else:
                                  pass # pre next piece checks failed
                          else:
                              pass # pre piece checks failed
                     
                    # check all possible roots.
                    #log.debug ("checking roots.")
                    for (lae,L) in self.roots:
                      l,r = remainder[:lae],remainder[lae:]
                      for eigenschaften in L.get(l,[]):
                          #log.debug ("trying root: %r with properties: %r", l,eigenschaften)
                          piece = Root(l,eigenschaften)
                          if check_PRE_ROOT(frag,piece,checks):
                              pChecks = piece.getChecks()
                              if check_PRE_PIECE(frag,piece,pChecks):
                                  if check_PRE_NEXT_PIECE(frag,piece,checks):
                                      # @TODO perhaps the next few lines could be faster and more elegant
                                      newChecks = mergeChecks(checks,pChecks)
                                      newChecks[HyphRule.PRE_PIECE] = []
                                      newChecks[HyphRule.PRE_NEXT_PIECE] = pChecks[HyphRule.PRE_NEXT_PIECE]
                                      newfrag = SuffixWordFrag(frag,piece)
                                      todo.append( (cword,newfrag,r,newChecks) )
                                      # Auch Verkürzung von 3 Konsonanten zu zweien berücksichtigen
                                      if KONSTANTEN_VERKUERZUNG_3_2 and l[-1]==l[-2] and l[-1] not in VOWELS:
                                          #log.debug ("konsonantenverkuerzung %s",l)
                                          newChecks = mergeChecks(checks,pChecks)
                                          newChecks[HyphRule.PRE_PIECE] = []
                                          # Konsonsantenverkürzung kommt nur bei Haupttrennstellen
                                          # vor, nicht vor Suffixes.
                                          newChecks[HyphRule.PRE_NEXT_PIECE] = [NO_SUFFIX()] + pChecks[HyphRule.PRE_NEXT_PIECE]
                                          newPiece = Root(l,eigenschaften)
                                          newfrag = SuffixWordFrag(frag,newPiece)
                                          newfrag.konsonantenverkuerzung_3_2 = True
                                          todo.append( (cword,newfrag,l[-1]+r,newChecks) )
                                  else:
                                      pass # pre next piece checks failed
                              else:
                                  pass # pre piece checks failed
                          else: # pre root checks failed
                              pass

                else: # fragment already has a root.
                    #log.debug ("checking suffixes.")
                    # check all possible suffixes.
                    for (lae,L) in self.suffixes:
                      l,r = remainder[:lae],remainder[lae:]
                      for eigenschaften in L.get(l,[]):
                          log.debug ("trying suffix: %r with properties: %s", l,eigenschaften)
                          piece = Suffix(l,eigenschaften)
                          pChecks = piece.getChecks()
                          if check_PRE_PIECE(frag,piece,pChecks):
                              if check_PRE_NEXT_PIECE(frag,piece,checks):
                                  # @TODO perhaps the next few lines could be faster and more elegant
                                  newChecks = mergeChecks(checks,pChecks)
                                  newChecks[HyphRule.PRE_PIECE] = []
                                  newChecks[HyphRule.PRE_NEXT_PIECE] = pChecks[HyphRule.PRE_NEXT_PIECE]
                                  newfrag = copy.copy(frag)
                                  newfrag.suffix = frag.suffix + [piece]
                                  todo.append( (cword,newfrag,r,newChecks) )
                                  
                              else:
                                  log.debug("pre next piece checks failed")
                                  pass # pre next piece checks failed
                          else:
                              log.debug("pre piece checks failed")
                              pass # pre piece checks failed
                     
                    # check suffix characters
                    if not frag.suffix_chars:
                        l = 0
                        while l<len(remainder) and remainder[l] in self.suffix_chars:
                            l = l+1
                        if l>0:
                            newfrag = frag.clone()
                            newfrag.suffix_chars = remainder[:l]
                            r = remainder[l:]
                            if check_PRE_WORD(cword,frag,checks) \
                            and check_PRE_NEXT_WORD(cword,frag,checks):
                                #log.debug ("@TODO: The above IF statement is definitely wrong.\n" + 
                                #    "We have to distinguish between the checks for CWORD and FRAG.\n" +
                                #    "Thus it seems that we need TWO check variables.")
                                chks = NO_CHECKS(HyphRule.AT_END) + checks[HyphRule.AT_END:]
                                todo.append ( (cword+[newfrag],None,r,chks) )
                                continue # do not examine the current state any more.
                            else: # checks failed
                                pass
                        else: # no suffix characters found
                            pass
                    else:
                        pass # we already have suffix characters.
            
        # Nothing more to do.
        if VERBOSE: log.info ("returning %r", solutions)
        return solutions

    # Hilfsfunktion
    def schiebe(self,offset,L):
        return [HyphenationPoint(h.indx+offset,h.quality,h.nl,h.sl,h.nr,h.sr) for h in L]

    def dudentrennung(self,wort,quality=None):
        """ 
            The algorithm how to hyphenate a word
            without knowing about the context.

            This code is quite specific to German!
            For other languages, there may be totally different rules.
            
            This rule is known as "Ein-Konsonanten-Regel" in German.
            The rule works (basically) as follows:
            First, find the vowels in the word,
            as they mark the syllables (one hyphenation point between
            two vowels (but consider sequences of vowels counting as one).
            If there are consonants between two vowels,
            put all but the last consonant to the left syllable,
            and only the last consonant to the right syllable
            (therefore the name one-consonant-rule).
            However, there are also sequences of consonants counting as one,
            like "ch" or "sch".
        """
        #print "dudentrennung: %s" % wort
        if not quality: quality = self.qNeben
        
        assert isinstance(wort, unicode)

        # Jede Silbe muss mindestens einen Vokal enthalten
        if len(wort) <= 2:
            return []
        # Suche bis zum ersten Vokal
        for vpos1 in range(len(wort)):
            if wort[vpos1] in VOWELS:
              if wort[vpos1-1:vpos1+1] != 'qu':
                break
        else:
            # Kein Vokal enthalten!
            return []
        # wort[vpos1] ist der erste Vokal
        fertig = False
        stpos = vpos1+1
        while not fertig:
            fertig = True
            # Suche bis zum zweiten Vokal
            for vpos2 in range(stpos,len(wort)):
                if wort[vpos2] in VOWELS:
                    break
            else:
                # Kein zweiter Vokal enthalten!
                return []
            # wort[vpos2] ist der zweite Vokal
            if vpos2==2 and wort[1] not in VOWELS:
                # Nach Einkonsonantenregel bleibt als erste Silbe nur ein einzelner Buchstabe,
                # z.B. o-ber. Das wollen wir nicht
                stpos = vpos2+1
                fertig = False
            if vpos2==vpos1+1:
                # a sequence of two vowels, like German "ei" or "au", or English "ou" or "oi"
                if wort[vpos1:vpos2+1] in [u'äu', u'au', u'eu', u'ei', u'ie', u'ee']:
                    # Treat the sequence as if it was one vowel!
                    stpos = vpos2+1
                    fertig = False
                else:
                    return [HyphenationPoint(vpos2,quality,0,self.shy,0,u"")] + self.schiebe(vpos2,self.dudentrennung(wort[vpos2:],quality))
        if wort[vpos2-3:vpos2] in [u'sch',]:
            return [HyphenationPoint(vpos2-3,quality,0,self.shy,0,u"")]     + self.schiebe(vpos2-3,self.dudentrennung(wort[vpos2-3:],quality))
        elif ALTE_REGELN and wort[vpos2-2:vpos2] in [u'st']:
            return [HyphenationPoint(vpos2-2,quality,0,self.shy,0,u"")]     + self.schiebe(vpos2-2,self.dudentrennung(wort[vpos2-2:],quality))
        elif ALTE_REGELN and wort[vpos2-2:vpos2] in [u'ck']:
            return [HyphenationPoint(vpos2-1,quality,1,u"k"+self.shy,0,u"")] + self.schiebe(vpos2-1,self.dudentrennung(wort[vpos2-1:],quality))
        elif wort[vpos2-2:vpos2] in [u'ch',u'ck', u'ph']:
            return [HyphenationPoint(vpos2-2,quality,0,self.shy,0,u"")]     + self.schiebe(vpos2-2,self.dudentrennung(wort[vpos2-2:],quality))
        elif wort[vpos2-1] in VOWELS:
            return [HyphenationPoint(vpos2  ,quality,0,self.shy,0,u"")]     + self.schiebe(vpos2,  self.dudentrennung(wort[vpos2:],quality))
        else:
            return [HyphenationPoint(vpos2-1,quality,0,self.shy,0,u"")]     + self.schiebe(vpos2-1,self.dudentrennung(wort[vpos2-1:],quality))

    def zerlegeWort(self,zusgWort,maxLevel=20):

        #Wort erstmal normalisieren
        assert isinstance(zusgWort,unicode)
        zusgWort = zusgWort.lower().replace(u'Ä',u'ä').replace(u'Ö',u'ö').replace(u'Ü',u'ü')
        lenword = len(zusgWort)
        #print zusgWort
        loesungen = []

        L = self._zerlegeWort(zusgWort)
        # Trennung für Wortstämme mit Endungen berichtigen
        for W in L:
            # Eine mögliche Lösung. Von dieser die einzelnen Wörter betrachten
            Wneu = []
            offset = 0
            ok = True
            #log.debug ("Versuche %r", W)
            sr = ""
            for i,w in enumerate(W):
                if not ok: break
                offset += len(w.prefix_chars)
                if i>0:
                    # @TODO: Hier darf nicht fest shy stehen, da
                    # das letzte Wort mit "-" geendet haben könnte
                    lastWordSuffixChars = W[i-1].suffix_chars
                    if lastWordSuffixChars and lastWordSuffixChars[len(lastWordSuffixChars)-1][-1:] in [u"-",self.shy]:
                        Wneu.append(HyphenationPoint(offset,self.qHaupt,0,"",0,sr))
                    else:
                        Wneu.append(HyphenationPoint(offset,self.qHaupt,0,self.shy,0,sr))
                if w.konsonantenverkuerzung_3_2:
                    sr = w.root.strval[-1]
                else:
                    sr = u""

                if w.prefix:
                    for f in w.prefix:
                        Wneu += self.schiebe(offset,self.dudentrennung(f.strval,self.qVorsilbe))
                        offset += len(f.strval)
                        Wneu.append(HyphenationPoint(offset,7,0,self.shy,0,u""))
                        # @TODO Qualität 7 ist hier fest eingebrannt
                for p in w.root.props:
                  if isinstance(p,TRENNUNG) or isinstance(p,KEEP_TOGETHER):
                    st = p.args
                    break
                else:
                    st = self.dudentrennung(w.root.strval,self.qSchlecht)
                if len(st):
                    Wneu += self.schiebe(offset,st)
                    st,stLast = st[:-1],st[-1]
                    p = stLast.indx
                    offset += p
                    en = w.root.strval[p:]+(u"".join([s.strval for s in w.suffix]))
                else:
                    en = w.root.strval+(u"".join([s.strval for s in w.suffix]))
                if w.suffix:
                    ent = self.dudentrennung(en,self.qNeben)
                    #print "en=",en,"ent=",ent
                    Wneu += self.schiebe(offset,ent)
                    # Prüfen, ob dieses Wort als letztes stehen muss
                #
                #for pf in w.prefix + [w.root] + w.suffix:
                #    if i>0 and pf.props.get(NOT_AFTER_WORD) and str(W[i-1].root) in pf.props.get(NOT_AFTER_WORD):
                #        if VERBOSE: print "'%s' nicht erlaubt nach '%s'" % (pf,W[i-1].root)
                #        ok = False
                #        break
                #    if pf.props.get(ONLY_LAST_WORD) and i<len(W)-1:
                #        if VERBOSE: print "'%s' nur als letztes Wort erlaubt!" % pf
                #        ok = False
                #        break
                #    if pf.props.get(ONLY_FIRST_WORD) and i>0:
                #        if VERBOSE: print "'%s' nur als erstes Wort erlaubt!" % pf
                #        ok = False
                #        break
                #else: 
                #  # letztes Wort
                #  for pf in w.prefix + [w.root] + w.suffix:
                #    #print "letztes Wort, Bestandteil",pf, pf.props
                #    if pf.props.get(NOT_LAST_WORD):
                #        if VERBOSE: print "'%s' nicht als letztes Wort erlaubt!" % pf
                #        ok = False
                #        break
                offset += len(en)
                offset += len(w.suffix_chars)
            if ok and (Wneu not in loesungen):
                log.debug ("Wneu=%r", Wneu)
                loesungen.append(Wneu)

        return loesungen
        
    def hyph(self,word):
        log.debug ("DCW hyphenate %r", word)
        assert isinstance(word, unicode)
        loesungen = self.zerlegeWort(word)
        if len(loesungen) > 1:
            # Trennung ist nicht eindeutig, z.B. bei WachsTube oder WachStube.
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
            if loesung:
                # Es gibt mindestens eine Trennstelle, die bei allen Varianten
                # enthalten ist, z.b. Wachstu-be.
                pass 
                # hword.info = ("HYPHEN_OK", loesung)
            else:
                # Es gibt keine Trennstelle.
                pass
        elif len(loesungen) == 1:
            # Trennung ist eindeutig
            loesung = loesungen[0]
            #hword.info = ("HYPHEN_OK", loesung)
            if not loesung:
                pass # hword.info = ("NOT_HYPHENATABLE", aWord)
        else:
            # Das Wort ist uns unbekannt.
            return None
        return HyphenatedWord(word, loesung)
        
    def i_hyphenate(self,aWord):
        return ExplicitHyphenator.i_hyphenate_derived(self, aWord)

if __name__=="__main__":
    h = DCWHyphenator("DE",5)
    h.test(outfname="DCWLearn.html")
