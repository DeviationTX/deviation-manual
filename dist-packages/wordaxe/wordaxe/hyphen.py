# -*- coding: iso-8859-1 -*-

__license__="""
   Copyright 2004-2008 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''

from copy import copy
SHY = "\xAD".decode("iso-8859-1")

class HyphenationPoint(object):
    """
    A possible hyphenation point in a HyphenatedWord.
    
    Attributes:
      indx        : The index where to split the word.
      quality     : The quality of this hyphenation point (0=bad,5=average,9=very good).
      nl,sl,nr,sr : Replacement parameters.
      
    Description:
      When we split the word at this hyphenation point,
      we can build the two strings left,right as follows:
      left = word[:pos-nl] + sl
      right = sr + word[pos+nr:]

    Some examples (where q is some quality, i.e. q=5):
    
      The usual case is nl=0,sl="\173",nr=0,sr="".
      In other words, just add a "shy" character to the left string.
      "Lesen" (to read) can be hyphenated as "le-" "sen":
      HyphenationPoint(2,q,0,"\173",0,"")
      
      In some cases, it is not necessary to add the shy character:
      "ABC-Buch" (ABC book) can be hyphenated as "ABC-" "buch":
      HyphenationPoint(4,q,0,"",0,"")
      
      And - especially using the OLD german rules - the case
      nl>0 or nr>0 can occur:
      
      The word "backen" (to bake) can be hyphenated between the "c" and the "k";
      however, the hyphenated version would be "bak-" "ken".
      Thus, the one and only hyphenation point in this word is
      HyphenationPoint(3,q,1,"k"+"\173",0,"")
      
      Another example: According to the old german rules, the word "Schiffahrt"
      is a concatenation of "Schiff" (ship) and "fahrt" (journey).
      The triple "f" is shortened to a double "f".
      But in case of hyphenation, it's three "f"s again: "Schiff-" "fahrt".
      HyphenationPoint(5,q,0,"f"+shy,0,"")
      This could also be expressed as HyphenationPoint(6,q,0,shy,0,"f").
    """
    __slots__ = ["indx","quality","nl","sl","nr","sr"]
    def __init__(self,indx,quality,nl=0,sl=u"",nr=0,sr=u""):
        self.indx = indx
        self.quality = quality
        self.nl = nl
        self.sl = unicode(sl)
        self.nr = nr
        self.sr = unicode(sr)
    def __str__(self):
        return 'HyphP(%d,%d)' % (self.indx,self.quality)
    def __repr__(self):
        return 'HyphenationPoint(%d,%d,%d,%s,%d,%s)' % (self.indx,self.quality,self.nl,`self.sl`,self.nr,`self.sr`)

def _lshift(hyphenations, amt):
    "Moves the hyphenation points left"
    hyph = []
    for h in hyphenations:
        if type(h) is int:
            if h > amt: 
                hyph.append(h-amt)
        else:
            if h.indx > amt:
                hyph.append(HyphenationPoint(h.indx-amt,h.quality,h.nl,h.sl,h.nr,h.sr))
    return hyph

class HyphenatedWord(unicode):
    """
    A hyphenated word.
    
    Attributes:
      word:         the word without hyphenations
      hyphenations: a list containing the possible hyphenation points.
      info:         Information about the hyphenation process.
    
    See also class Hyphenator for an explanation.
    """

    __slots__ = ["hyphenations",]
    
    def __new__(klass, word, hyphenations=None, encoding="utf-8", errors='strict'):
        if isinstance(word, unicode):
            o = unicode.__new__(klass, word)
        else:
            o = unicode.__new__(klass, word, encoding, errors)
        if hyphenations is not None:
            o.hyphenations = hyphenations
        elif hasattr(word, "hyphenations"):
            o.hyphenations = word.hyphenations
        else:
            raise ValueError("'hyphenations' Argument is missing")
        return o
            
    def __str__(self):
        return self.encode("utf-8")

    def __repr__(self):
        return ("HyphenatedWord(%s)" % super(HyphenatedWord, self).__repr__())

    def __add__(self, other):
        """(other) -> instance of this class
        Like unicode.__add__, but assumes that the other element
        is either unicode or an utf-8 encoded string.
        """
        if not isinstance(other,unicode):
            other = unicode(other, "utf-8")
        return unicode(unicode.__add__(self, other))

    def __radd__(self, other):
        """(other) -> instance of this class
        Like unicode.__add__, but assumes that the other element
        is either unicode or an utf-8 encoded string.
        """
        if isinstance(other, basestring):
            if not isinstance(other,unicode):
                other = unicode(other, "utf-8")
            return unicode(unicode.__add__(other, self))
        else:
            return NotImplemented

    def split(self, hp):
        """Performs a split at the given hyphenation point.
        
           Returns a tuple (left,right)
           where left is a string (the left part, including the hyphenation character)
           and right is a HyphenatedWord describing the rest of the word.
        """
        if type(hp) is int:
            left = self[:hp] + SHY
            hyph = _lshift (self.hyphenations, hp)
            print hyph
            right = self.__class__(self[hp:], hyphenations=hyph)
        else:
            shift = hp.indx-hp.nr+len(hp.sr)
            left = self[:hp.indx-hp.nl] + hp.sl
            hyph = _lshift (self.hyphenations, shift)
            right = self.__class__(hp.sr+self[hp.indx+hp.nr:], hyphenations=hyph)
        assert isinstance(left, unicode)
        assert isinstance(right, self.__class__)
        return (left,right)
        
    def prepend(self, string):
        "Allows adding prefix chars (such as '('), returning a new HyphenatedWord"
        return self.__class__(unicode(string) + self, hyphenations=_lshift(self.hyphenations,-len(string)))

    def append(self, string):
        "Allows adding suffix chars (such as ')'), returning a new HyphenatedWord"
        return self.__class__(self + unicode(string), hyphenations=self.hyphenations)
            
    def showHyphens(self):
        "Returns the possible hyphenations as a string list, for debugging purposes."
        L = []
        for h in self.hyphenations:
            left,right = self.split(h)
            L.append(u"%s %s (%d)" % (left,right, h.quality))
        return L
        
    def get_hyphenations(self):
        "Returns an iteration of the possible hyphenations."
        for hp in self.hyphenations:
            yield self.split(hp)
                
    @staticmethod 
    def join(*hyphwords):
        """
        Create a new hyphenated word from a list of other hyphenated words.
        a = HyphenatedWord("Vogel")    # Vo-gel
        b = HyphenatedWord("grippe")   # grip-pe
        Inserts a good quality hyphenation point at the boundaries.
        c = HyphenatedWord.join(a,b)
        # Vo-gel=grip-pe.
        """
        if len(hyphwords) == 1:
            hyphwords = hyphwords[0]
        for w in hyphwords:
            assert isinstance(w,HyphenatedWord)
        word = u"".join(hyphwords)
        hps = []
        offset = 0
        for w in hyphwords:
            hps += _lshift(w.hyphenations, -offset)
            if w is not hyphwords[-1]:
                #print w.word
                if w.endswith(u"-") or w.endswith(SHY):
                    hps.append(HyphenationPoint(offset+len(w), quality=9))
                else:
                    hps.append(HyphenationPoint(offset+len(w), quality=9, sl=SHY))
                offset += len(w)
        return HyphenatedWord(word, hyphenations=hps)

class Hyphenator:
    """
    Hyphenator serves as the base class for all hyphenation implementation classes.
    
    Some general thoughts about hyphenation follow.
    
    Hyphenation is language specific.
    Hyphenation is encoding specific.
    Hyphenation does not use the context of a word.
    Good Hyphenation enables the reader to read fluently,
    bad hyphenation can make a word hard to read.
    
    Hyphenation is language specific:
    The same word may be valid in several languages,
    and the valid hyphenation points can depend on the language.
    Example: Situation
   
    Hyphenation is encoding specific:
    This is just an implementation detail really,
    however an important one.
    For example, every hyphenation algorithm uses some internal
    encoding scheme, and it should document this scheme.
    How is the input encoding and the output encoding?
    
    Hyphenation does not use the context of the word:
    Surely, it could make sense to "understand" the context.
    There may be some words that should be hyphenated differently
    depending on the context.
    But this would make a really BIG overhead;
    and I can't really think of an example. It's not worth thinking about it.
    
    Good Hyphenation enables the reader to read fluently,
    bad hyphenation can make a word hard to read.
    Some languages, for example german, make frequent use of
    the concatenation of several simple words to build more complex words,
    like "Hilberts Nullstellensatz" (something I remember from Algebra).
    Null = Zero
    Stelle = Place, Location
    Satz = Theorem (math)
 
    The one famous example for bad german hyphenation is the word "Urinstinkt".
    This is made up of
    Ur = Primal
    Instinkt = Instinct
    Hyphenatiing this word in a valid, but unfortunate position,
    yields "Urin-stinkt" (urine stinks).
   
    These thoughts have led to the following interface for hyphenation.
    """
   
    def __init__ (self, language, minWordLength=4, codec=None, shy=SHY, **options):
        """
        Creates a new hyphenator instance for the given language.
        In this base class, the language arguments serves only for
        information purposes.
        Words shorter than minWordLength letters will never be considererd 
        for hyphenation.
        """
        self.language = language
        self.minWordLength = 4
        assert isinstance(shy, unicode)
        self.shy = shy
        self.options = options
        
        """
        self.codec = codec
        if self.codec is None:
            import encodings.latin_1
            self.codec = encodings.latin_1.Codec()
        """
    """        
    def getCodec(self):
        return self.codec
    """
        
    def getLanguage(self):
        return self.language
        
    def getMinWordLength(self):
        return self.minWordLength
        
    def setMinWordLength(self,nLength):
        if type(nLength)==int and nLength>2 and nLength<100:
            self.minWordLength = nLength
        else:
            raise ValueError, nLength
            
    def __repr__(self):
        #return "%s(%s,%d,%s)" % (str(self.__class__),self.language,self.minWordLength,self.codec)
        return "%s(%s,%d)" % (str(self.__class__),self.language,self.minWordLength)
    
    def postHyphenate(self,hyphenatedWord):
        """This function is called whenever hyphenate has been called.
           It can be used to do some logging,
           or to add unknown words to a dictionary etc.
        """
        if hyphenatedWord is not None:
            assert isinstance(hyphenatedWord, HyphenatedWord)
            assert type(hyphenatedWord.hyphenations) == list

    def i_hyphenate(self, aWord):
        """
        This base class does not support any hyphenation!
        """
        return None
            
    def hyphenate(self,aWord):
        """
        Finds possible hyphenation points for a aWord, returning a HyphenatedWord
        or None if the hyphenator doesn't know the word.
        """
        assert isinstance(aWord,unicode)
        hword = self.i_hyphenate(aWord)
        self.postHyphenate(hword)
        return hword
        
class Cached(Hyphenator):
    """
    This caches the results of the hyphenate function.
    Use it if the hyphenation is too slow.
    """
    
    def __init__(self, hyphenator, max_entries):
        """
        Creates a new, cached version of hyphenator
        that caches at most max_entries of the results
        from hyphenator.hyphenate.
        If you need other functionality of the hyphenator,
        you have to access the attribute "hyphenator"
        directly.
        """
        self._max_entries = max_entries
        assert isinstance(hyphenator, Hyphenator)
        self.hyphenator = hyphenator
        self.cache = dict()
        
    def hyphenate(self, aWord):
        """
        Get the hyphenated word for word from the cache.
        If not found there, call the internal hyphenator
        and add to the cache (like a lazy setdefault).
        """
        cache = self.cache
        if aWord not in cache:
            if len(cache) >= self._max_entries:
                self.cache = dict()
            self.cache[aWord] = self.hyphenator.hyphenate(aWord)
        return self.cache[aWord]

    def purge_cache(self):
        """
        Purges the cache (freeing resources).
        """
        self.cache = dict()
