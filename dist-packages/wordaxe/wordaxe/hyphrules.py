# -*- coding: iso-8859-1 -*-

__license__="""
   Copyright 2004-2008 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''

import logging
logging.basicConfig()
log = logging.getLogger("HyphRules")
log.setLevel(logging.WARNING)

from wordaxe.hyphen import SHY, HyphenationPoint

class AlgorithmError(Exception):
    pass

def decodeTrennung(t):
    """Hyphenates a word whose hyphenation point are explicitly given.
       For example "play5er".
    """
    W=[]
    p=0
    for i in range(len(t)):
        if t[i] in "123456789":
            q = int(t[i])
            W.append(HyphenationPoint(p,q,0,SHY,0,u""))
        else:
            p += 1
    return W

class HyphRule:
    """Definition of a rule for hyphenation.
    """
    name = "generic hyphenation rule - do not use directly"
    
    # When to check this rule (in chronological order):
    PRE_PIECE       = 0 # before adding this piece to the WordFrag
    PRE_ROOT        = 1 # before adding the root of the wordFrag (without knowing the root)
    PRE_NEXT_PIECE  = 2 # before adding the next piece to the WordFrag
    PRE_WORD        = 3 # before adding the WordFrag as a word to the compound word
    PRE_NEXT_WORD   = 4 # before adding the next word to the compound word
    AT_END          = 5 # when the compound word is complete
    
    def __init__(self,when):
        self.when = when
        self.args = ""
    
    def check(self,wfrag,when):
        """Check if a give word fulfills this rule.
        """
        raise AlgorithmError
        
    def __str__(self):
        return self.name + " " + self.args

    def __repr__(self):
        return "HyphRule(%s %r)" % (self.name, self.args)

class NEED_PREFIX(HyphRule):
    """The given wordfrag needs a prefix
       (any or one of those given in args).
    """
    name = "NEED_PREFIX"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_PIECE])
        if args:
            self.allowedPrefixes = " "+args+" "
        else:
            self.allowedPrefixes = None

    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_PIECE:
            if not wfrag.prefix:
                return False
            if self.allowedPrefixes:
                log.debug ("allowedPrefixes: %r", self.allowedPrefixes)
                for p in wfrag.prefix:
                    if " "+p.strval+" " in self.allowedPrefixes:
                        return True
                return False
            return True
        raise AlgorithmError

class NO_PREFIX(HyphRule):
    """The given wordfrag must not contain any prefix.
       (if args is given, args must not contain any of the wordfrag's prefixes).
    """
    name = "NO_PREFIX"

    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_PIECE])
        self.forbiddenPrefixes = " "+args+" "

    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_PIECE:
            if wfrag.prefix:
                return False
            if self.forbiddenPrefixes:
                for p in wfrag.prefix:
                    if " "+p.strval+" " in self.allowedPrefixes:
                        return False
                return True
        raise AlgorithmError

class NEED_SUFFIX(HyphRule):
    """The given wordfrag needs a suffix.
    """
    name = "NEED_SUFFIX"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_NEXT_PIECE])
        if args: raise ValueError

    def check(self,wfrag,when,nextPiece=None):
        #log.debug ("when=%d, nextPiece=%r", when, nextPiece)
        if when==HyphRule.PRE_NEXT_PIECE:
            assert isinstance(nextPiece,Suffix)
            return True
        raise AlgorithmError

class NO_SUFFIX(HyphRule):
    """The given wordfrag must not have any suffix.
    """
    name = "NO_SUFFIX"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_NEXT_PIECE])
        if args: raise ValueError

    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_NEXT_PIECE:
            assert isinstance(nextPiece,Suffix), repr(nextPiece.strval)
            return False
        raise AlgorithmError

class ForeignWordRule(HyphRule):
    """A helper class for ENGLISCH and FREMDWORT (foreign words from different languages)"""
    name = "ForeignWordRule"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_PIECE,HyphRule.PRE_NEXT_PIECE])
        if args: raise ValueError

    def check(self,wfrag,when,nextPiece=None):
        log.debug("%s check %r,%s,%s", self.__class__, wfrag, when, nextPiece)
        if when==HyphRule.PRE_PIECE:
            if not wfrag.root: # called for a prefix or the root
                log.debug("PRE_PIECE called for a prefix or the root")
                if isinstance(nextPiece,Root):
                    setattr(wfrag,self.name,True)      # notify the suffixes
                    log.debug("Attribut %s gesetzt bei Objekt %s %s", self.name, wfrag.__class__, id(wfrag))
                return True
            else:               # called for a suffix
                log.debug("PRE_PIECE called for a suffix")
                log.debug("self.name=%s", self.name)
                log.debug("wfrag.id=%s, wfrag.dir=%s", id(wfrag), dir(wfrag))
                return hasattr(wfrag,self.name)
        elif when==HyphRule.PRE_NEXT_PIECE:
            if isinstance(nextPiece,Root):    # called for the last prefix
                for prop in nextPiece.props:           # return True iff the root is a FREMDWORT
                    if prop.name ==self.name:  
                        return True
                return False
            return True                                # called for anything else but the last prefix
        raise AlgorithmError

class ENGLISCH(ForeignWordRule):
    """The given wordfrag is ENGLISCH (coming from English).
      Therefore different prefixes and suffixes can be checked.
      If this is defined for the last prefix in a wordfrag, then the root must be ENGLISCH, too.
      If this is defined for a Suffix, then the root must be ENGLISCH, too.
    """
    name = "ENGLISCH"
    
    def __init__(self,args=""):
        ForeignWordRule.__init__(self,args)

class FREMDWORT(ForeignWordRule):
    """The given wordfrag is a FREMDWORT (coming from Greek or Latin).
      Therefore different prefixes and suffixes can be checked.
      If this is defined for the last prefix in a wordfrag, then the root must be FREMDWORT, too.
      If this is defined for a Suffix, then the root must be FREMDWORT, too.
    """
    name = "FREMDWORT"
    
    def __init__(self,args=""):
        ForeignWordRule.__init__(self,args)

class ONLY_FIRST(HyphRule):
    """This prefix (resp. suffix) must be the first prefix (resp. suffix).
    """
    name = "ONLY_FIRST"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_PIECE])
        if args: raise ValueError

    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_PIECE:
            log.debug("ONLY_FIRST  PRE_PIECE chk, wfrag=%s, nextPiece=%s", wfrag, nextPiece)
            if isinstance(nextPiece,Prefix):
                return (not wfrag.prefix)
            elif isinstance(nextPiece,Suffix):
                return (not wfrag.suffix)
        raise AlgorithmError

class ONLY_LAST(HyphRule):
    """This prefix (resp. suffix) must be the last prefix (resp. suffix).
    """
    name = "ONLY_LAST"

    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_NEXT_PIECE])
        if args: raise ValueError

    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_NEXT_PIECE:
            if isinstance(nextPiece,Prefix) \
            or isinstance(nextPiece,Suffix):
                return False
            return True
        raise AlgorithmError

class ONLY_FIRST_WORD(HyphRule):
    """This word must be the first word in a compound word.
    """
    name = "ONLY_FIRST_WORD"

    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_WORD])
        if args: raise ValueError

    def check(self,compWord,when,nextPiece=None):
        if when==HyphRule.PRE_WORD:
            return compWord==[]
        raise AlgorithmError        

class ONLY_LAST_WORD(HyphRule):
    """This word must be the last word in a compound word.
    """
    name = "ONLY_LAST_WORD"

    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_NEXT_WORD])
        if args: raise ValueError

    def check(self,compWord,when,nextPiece=None):
        if when==HyphRule.PRE_NEXT_WORD:
            return False
        raise AlgorithmError        

class NOT_AFTER_WORD(HyphRule):
    """This word must not follow any of the words given in args.
    """
    name = "NOT_AFTER_WORD"

    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_WORD])
        self.args = " "+args+" "

    def check(self,compWord,when,nextPiece=None):
        if when==HyphRule.PRE_WORD:
            if compWord and " "+compWord[-1].root.strval+" " in self.args:
                return False
            return True
        raise AlgorithmError        

class NOT_LAST_WORD(HyphRule):
    """This word must not be the last word in a compound word.
    """
    name = "NOT_LAST_WORD"

    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_NEXT_WORD,HyphRule.AT_END])
        if args: raise ValueError

    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_NEXT_WORD:
            if not wfrag:
                return True # log.error ("NOT_LAST_WORD: wfrag=%r", wfrag)
            else:
                setattr(wfrag[-1],self.name,True)
            return True
        elif when==HyphRule.AT_END:
            return hasattr(wfrag[-1],self.name)
        raise AlgorithmError, when        

class SINGLE_WORD(HyphRule):
    """This word must be the only one in a compound word.
    """
    name = "SINGLE_WORD"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_WORD,HyphRule.PRE_NEXT_WORD])
        if args: raise ValueError

    def check(self,compWord,when,nextPiece=None):
        if when==HyphRule.PRE_WORD:
            return compWord==[]
        elif when==HyphRule.PRE_NEXT_WORD:
            return False
        raise AlgorithmError        

class ONLY_AFTER(HyphRule):
    """This piece may only follow immediately after one of the pieces given in args.
    """
    name = "ONLY_AFTER"
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_PIECE])
        self.args = " "+args+" "
    
    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_PIECE:
            if isinstance(nextPiece,Prefix):
                return wfrag.prefix and (" "+wfrag.prefix[-1].strval+" " in self.args)
            elif isinstance(nextPiece,Suffix):
                return wfrag.suffix and (" "+wfrag.suffix[-1].strval+" " in self.args) 
            # not allowed for Root
        raise AlgorithmError

class NOT_AFTER(HyphRule):
    """This piece must not follow immediately after any of the pieces given in args.
    """
    name = "NOT_AFTER"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_PIECE])
        self.args = " "+args+" "
    
    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_PIECE:
            if isinstance(nextPiece,Prefix):
                return not (wfrag.prefix and (" "+wfrag.prefix[-1].strval+" " in self.args))
            elif isinstance(nextPiece,Suffix):
                return not (wfrag.suffix and (" "+wfrag.suffix[-1].strval+" " in self.args))
            # not allowed for Root
        raise AlgorithmError

class NOT_BEFORE(HyphRule):
    """This piece must not stand immediately before any of the pieces given in args.
    """
    name = "NOT_BEFORE"
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_NEXT_PIECE])
        self.args = " "+args+" "
    
    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_NEXT_PIECE:
            if isinstance(nextPiece,Prefix):
                return not (wfrag.prefix and (" "+wfrag.prefix[-1].strval+" " in self.args))
            elif isinstance(nextPiece,Suffix):
                return not (wfrag.suffix and (" "+wfrag.suffix[-1].strval+" " in self.args))
            else:
                return True  # don't check the rule for the last prefix (nextPiece is the Root).
        raise AlgorithmError

class TRENNUNG(HyphRule):
    """The hyphenation for this root (or a special word)
       is given explicitly (don't use Duden-Algorithm).
       This rule is special, because there is a hard-coded
       reference to it in the algorithm.
    """
    name = "TRENNUNG"
    
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.AT_END])
        self.args = decodeTrennung(args)
        
    def check(self,wfrag,when,nextPiece=None):
        return True

class KEEP_TOGETHER(TRENNUNG):
    """Do not hyphenate inside this root (or special word).
    """
    name = "KEEP_TOGETHER"
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.AT_END])
        assert args==""
        self.args = []
        
    def check(self,wfrag,when,nextPiece=None):
        return True

class NOT_BEFORE_CHAR(HyphRule):
    """This piece must not stand before one of the characters in args.
    """
    name = "NOT_BEFORE_CHAR"
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_NEXT_PIECE])
        self.args = args
        
    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_NEXT_PIECE:
            return nextPiece.strval[0] not in self.args
        raise AlgorithmError

class NOT_AFTER_CHAR(HyphRule):
    """This piece must not follow after any of the characters in args.
    """
    name = "NOT_AFTER_CHAR"
    def __init__(self,args=""):
        HyphRule.__init__(self,[HyphRule.PRE_PIECE])
        self.args = args
        
    def check(self,wfrag,when,nextPiece=None):
        if when==HyphRule.PRE_PIECE:
            if wfrag.suffix:
                return wfrag.suffix[-1].strval[-1] not in self.args
            elif wfrag.root:
                return wfrag.root.strval[-1] not in self.args
            elif wfrag.prefix:
                return wfrag.prefix[-1].strval[-1] not in self.args
        raise AlgorithmError

rulelist = [ NEED_PREFIX, NO_PREFIX,
             NEED_SUFFIX, NO_SUFFIX,
             ENGLISCH, FREMDWORT,
             ONLY_FIRST, ONLY_LAST,
             ONLY_FIRST_WORD, ONLY_LAST_WORD, NOT_AFTER_WORD, NOT_LAST_WORD, SINGLE_WORD,
             ONLY_AFTER, NOT_AFTER,
             NOT_BEFORE,
             TRENNUNG, KEEP_TOGETHER,
             NOT_BEFORE_CHAR, NOT_AFTER_CHAR,
           ]

RULES = dict([(r.name,r) for r in rulelist])

def NO_CHECKS(siz=6):
    return [list() for x in range(siz)]

class StringWithProps:
    """A string with properties."""
    __slots__ = ["strval", "props"]
    def __init__(self,s,p):
        self.strval = s
        self.props = p
    def __str__(self):
        #raise ValueError
        return self.strval
        
    def getChecks(self):
        """return a 6-element list, where each element is a list of HyphRules:
           [PRE_PIECE checks, PRE_ROOT checks, PRE_NEXT_PIECE checks,
            PRE_WORD checks, PRE_NEXT_WORD checks, AT_END checks].
        """
        chks=NO_CHECKS()
        for p in self.props:
            for w in p.when:
                chks[w].append(p)
        return chks

class Prefix(StringWithProps):
    pass

class Root(StringWithProps):
    pass

class Suffix(StringWithProps):
    pass
