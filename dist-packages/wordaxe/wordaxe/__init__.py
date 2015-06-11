# -*- coding: iso-8859-1 -*-

__license__="""
   Copyright 2004-2010 Henning von Bargen (henning.vonbargen arcor.de)
   This software is dual-licenced under the Apache 2.0 and the
   2-clauses BSD license. For details, see license.txt in the doc directory.
"""

__version__=''' $Id: __init__.py,v 1.2 2004/05/31 22:22:12 hvbargen Exp $ '''
__doc__='Hyphenation support using different algorithms'

__all__ = ["BaseHyphenator", "DCWHyphenator", "PyHnjHyphenator", "SHY", "HyphenationPoint", "HyphenatedWord"]

from wordaxe.hyphen import SHY, HyphenationPoint, HyphenatedWord, Hyphenator, Cached

# This is meant as a registry for Hyphenators.
# if you want to use a Hyphenator A for language B,
# just set hyphRegistry[A]=B
hyphRegistry = {}

version = "wordaxe 1.0.1"
