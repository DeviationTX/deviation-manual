import os, re
from sphinx import addnodes
from sphinx.directives.other import Include as BaseInclude
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList

# This module parses the source code after it has been read in but before
# it goes to docutils for tokenizing
# We look for sections blocked by 'ignoreunless' to 'stopignore' that don't match
# any provided tags and removethese sections
#
# Because 'include' directives are handled later in the flow, we also override
# The include directive and apply the same filtering to the output
#
# The include parser uses the state machine, which I don't really understand
# So instead we directly manipulate the internal structures of the state machine
# to remove the unwanted sections (eww).  This will be very brittle

myapp = None
 
def setup(app):
    global myapp
    app.ignore = []
    app.add_config_value('pp_macros', {}, "env")
    app.connect('source-read', source_read_handler)
    myapp = app

def remove_from_list(app, lines):
    startignore = re.compile(ur'^\.\. ignoreunless::\s+(\S+)')
    stopignore  = re.compile(ur'^\.\. stopignore::')
    macro       = re.compile(ur'^\.\. macro::\s+(\S+)')
    inline      = re.compile(ur'::(\S+)::')

    def inline_repl(matchobj):
        if matchobj.group(1) in app.config.pp_macros:
            print "Matched " + matchobj.group(0) + " to " + matchobj.group(1) +" => " + app.config.pp_macros[matchobj.group(1)]
            return app.config.pp_macros[matchobj.group(1)]
        else:
            print "Ignoring " + matchobj.group(0)
            return matchobj.group(0)

    matched = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if stopignore.match(line):
            matched = 0
            del lines[i]
            continue
        if matched == 1:
            #print("Discarding: " + line);
            del lines[i]
            continue
        m = startignore.match(line)
        if m:
            if not app.tags.has(m.group(1)):
                matched = 1
            del lines[i]
            continue

        if not isinstance(lines, StringList):
            line = inline.sub(inline_repl, line)
            lines[i] = line
        else:
            line = inline.sub(inline_repl, line)
            lines[i] = line

        m = macro.match(line)
        if m:
            if m.group(1) in app.config.pp_macros:
                new_lines = app.config.pp_macros[m.group(1)].split('\n');
                if isinstance(lines, StringList):
                    source = lines.source(i)
                    # print("Found StringList: " + lines[i] + " Source: " + source)
                del lines[i]
                for newline in new_lines:
		    if isinstance(lines, StringList):
                        lines.insert(i, newline, source=source)
                    else:
                        lines.insert(i, newline)
                    i = i + 1
        i = i + 1

def source_read_handler(app, docname, source):
    lines = source[0].split('\n')
    remove_from_list(app, lines)
    source[0] = '\n'.join(lines)

class Include(BaseInclude):
    """
    Like the standard "Include" directive, but interprets absolute paths
    "correctly", i.e. relative to source directory.
    """


    def run(self):
        global myapp
        ret = BaseInclude.run(self)
        remove_from_list(myapp, self.state_machine.input_lines)
        return ret

directives.register_directive('include', Include) 
