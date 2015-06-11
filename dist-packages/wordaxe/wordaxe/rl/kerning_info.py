#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# Kerning info

import os
import sys
from reportlab.pdfbase import ttfonts
import struct
import bisect

def extract_kerning_table(face):
    "Extract the Kerning table from a TrueType font"
    try:
        raw_data = face.get_table("kern")
    except KeyError:
        # Font does not contain a kerning table
        return []
    version, nTables = struct.unpack_from(">HH", raw_data)
    #print "version:", version
    #print "nTables:", nTables
    offset = 4
    for subtable_no in range(nTables):
        #print "subtable %s" % subtable_no
        version, length, coverage = struct.unpack_from(">HHH", raw_data, offset)
        #print "version:", version
        #print "length:", length
        #print "coverage:",coverage
        horizontal = bool(coverage & 1)
        minimum = bool(coverage & 2)
        cross_stream = bool(coverage & 4)
        override = bool(coverage & 8)
        format = coverage >> 8
        #print "horizontal:", horizontal
        #print "minimum:", minimum
        #print "cross_stream:", cross_stream
        #print "override", override
        #print "format:", format    
        o = offset + 6
        if format == 0:
            nPairs, searchRange, entrySelector, rangeShift = struct.unpack_from(">4H", raw_data, o)
            #print "nPairs:", nPairs
            #print "searchRange:", searchRange
            #print "entrySelector:", entrySelector
            #print "rangeShift:", rangeShift
            o += 8
            # TODO can this be done more efficient using struct?
            pairs = []
            for entry in range(nPairs):
                pair = struct.unpack_from(">HHh", raw_data, o)
                pairs.append(pair)
                o += 6
            #print "pairs:", pairs
        else:
            print "Kerning subtable format %s not supported." % format
        offset += length
        assert o == offset
        return pairs
    
def glyf(face, ch):
    "Glyph index of ch"
    return face.charToGlyph[ord(ch)]
    
def kerning(face, a, b):
    """
    Returns the kerning for the characters a and b and the font face.
    The return value is given in em/1000(?).
    """
    unitsPerEm = getattr(face, "unitsPerEm", 0)
    if not unitsPerEm:
        return 0.
    scale = lambda x, unitsPerEm=unitsPerEm: x * 1000. / unitsPerEm
    kerning_table = getattr(face, "kerning_table", None)
    if kerning_table is None:
        kerning_table = extract_kerning_table(face)
        setattr(face, "kerning_table", kerning_table)
    gl_a = glyf(face, a)
    gl_b = glyf(face, b)
    i = bisect.bisect(kerning_table, (gl_a, gl_b, None))
    if i == len(kerning_table):
        return 0.
    l, r, k = kerning_table[i]
    if l == gl_a and r == gl_b:
        return scale(k)
    else:
        return 0.
    
def kerning_pairs(face, s):
    """
    Compute the Kerning values for the character-pairs of the string s.
    """
    if not s:
        return []
    result = []
    old = s[0]
    for ch in s[1:]:
        result.append(kerning(face, old, ch))
        old = ch
    #print "kerning_pairs(%r) = %r" % (s, result)
    return result

#print kerning_pairs(font.face, "MAYA")
#print kerning_pairs(font.face, "VASE")
#print kerning_pairs(font.face, "Vaya con dios")

def stringWidth_kerning(font, text, size, encoding='utf-8'):
    """
    see TTFont.pyStringWidth, but takes kerning into account
    """
    if not isinstance(text,unicode):
        text = unicode(text, encoding or 'utf-8')   # encoding defaults to utf-8
    face = font.face
    g = face.charWidths.get
    dw = face.defaultWidth
    kp = kerning_pairs(face, text)
    return 0.001*size*(sum([g(ord(u),dw) for u in text]) + sum(kp))


import new
ttfonts.TTFont.stringWidth_kerning = new.instancemethod(stringWidth_kerning,None,ttfonts.TTFont)
    
if __name__ == "__main__":
    fname = r"c:\windows\fonts\arial.ttf"
    font = ttfonts.TTFont("Arial", fname)
    face = font.face
    print kerning(font.face, 'A', 'V')
    print kerning(font.face, 'A', 'A')
    print kerning(font.face, 'A', 'v')
    for text in ["Maya", "Vase", "Kandelaber", "Kronjuwelen", "Vaya con dios"
            ]:
        print text,
        print "without Kerning:", font.stringWidth(text, 12),
        print "with    Kerning:", font.stringWidth_kerning(text, 12)
