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
    startignore = re.compile(u'^\.\. if::\s+(\S+)')
    changeignore= re.compile(u'^\.\. elseif::\s+(\S+)')
    stopignore  = re.compile(u'^\.\. endif::')
    macro       = re.compile(u'^\.\. macro::\s+(\S+)\s*(.*\S)?')
    inline      = re.compile(u'\|(\S+)\|')

    def inline_repl(matchobj):
        if matchobj.group(1) in app.config.pp_macros:
            #print "Matched " + matchobj.group(0) + " to " + matchobj.group(1) +" => " + app.config.pp_macros[matchobj.group(1)]
            return app.config.pp_macros[matchobj.group(1)]
        else:
            #print "Ignoring " + matchobj.group(0)
            return matchobj.group(0)

    # 0: not in conditional
    # 1: in conditional but ignoring it
    # 2: in conditional but parsing it
    # 3: ignore all other conditions in this block
    in_cond = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if in_cond > 0:
            # inside conditional
            if stopignore.match(line):
                in_cond = 0
                del lines[i]
                continue
            m = changeignore.match(line)
            if m:
                if in_cond == 2:
                    in_cond = 3
                elif in_cond == 1:
                    in_cond = 2 if app.tags.has(m.group(1)) else 1
                del lines[i]
                continue
        if in_cond == 1 or in_cond == 3:
            # inside conditional but tag did NOT match
            #print("Discarding: " + line);
            del lines[i]
            continue
        if in_cond == 0:
            m = startignore.match(line)
            if m:
                in_cond = 2 if app.tags.has(m.group(1)) else 1
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
                replace_str = app.config.pp_macros[m.group(1)]
                if m.group(2):
                    # macro takes options to be replaced
                    varmap = {}
                    idx = 1
                    #print("start: " + replace_str)
                    for g in m.group(2).split():
                       #print"replacing ':VAL" + str(idx) + "' with '" + g + "'"
                       replace_str = replace_str.replace(":VAL"+str(idx)+":", g)
                       idx = idx + 1
                    #print("end: " + replace_str)
                new_lines = replace_str.split('\n')
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
