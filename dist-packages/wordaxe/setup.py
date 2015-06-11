#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup


setup(
    name = "wordaxe",
    version = "1.0.1",
    description = "Provide hyphenation for python programs and ReportLab paragraphs.",
    long_description = "Provide hyphenation for python programs and ReportLab paragraphs.",
    author = "Henning von Bargen",
    author_email = "henning.vonbargen@arcor.de",
    maintainer = "Henning von Bargen",
    maintainer_email = "henning.vonbargen@arcor.de",
    license = ["Apache License, version 2.0", "Free BSD License"],
    platforms = ["Unix", "Windows", "generic"],
    keywords = ["multi-language", "text processing", "hyphenation", "paragraphs", "reportlab"],
    url = "http://deco-cow.sourceforge.net",
    download_url = "http://sourceforge.net/project/platformdownload.php?group_id=105867",
    packages = ["wordaxe", "wordaxe/rl", "wordaxe/plugins", "wordaxe/dict"],
    package_data = {"wordaxe": ["dict/*.dic" ]}
)


# Backup original Reportlab's file rl_codecs.py -> rl_codecs.py.bak
# and replace the original with the one in hyphenation/rl if needed.

import sys

setupCommand = sys.argv[-1]

if setupCommand == "install":

    from shutil import copy2
    try:
        from hashlib import md5
    except ImportError: # Python < 2.5
        from md5 import new as md5

    def fileHash(path):
        """Return MD5 hash of an entire file."""
        h = md5()
        h.update(open(path, "rb").read())
        return h.hexdigest()

    try:
        import reportlab
        if reportlab.Version <= "2.3":
            from reportlab.pdfbase import rl_codecs
            src = rl_codecs.__file__
            if src.endswith(".pyc"):
                src = src[:-1]
            new = "wordaxe/rl/rl_codecs.py"
            if fileHash(src) != fileHash(new):
                bak = src + ".bak"
                print "backing up %s -> %s" % (src, bak)
                copy2(src, bak)
                print "copying %s -> %s" % (new, src)
                copy2(new, src)
            else:
                print "no update of '%s' needed" % src
    except ImportError:
        print "Note: ReportLab is not properly installed."

