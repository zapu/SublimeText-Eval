'''
Fork of NodeEval

now evaluates some other stuff too

'''

import sublime, sublime_plugin, os, time, threading
from functools import partial
from subprocess import Popen, PIPE, STDOUT

settingsFilename = "Evals.sublime-settings"

# 
# Globals
# 
g_lastCwd = None


#
# Create a new output, insert the message and show it
#
def panel(view, message, region, syntax):
  s = sublime.load_settings(settingsFilename)
  window = view.window()
  # Should we set the clipboard?
  clipboard = s.get('copy_to_clipboard')
  if clipboard: sublime.set_clipboard( message )
  # determine the output format
  output = s.get('output')
  clear = s.get('overwrite_output')

  # Output to a Console (panel) view
  if output == 'console':
    p = window.get_output_panel('nodeeval_panel')
    p_edit = p.begin_edit()
    p.insert(p_edit, p.size(), message)
    p.end_edit(p_edit)
    p.show(p.size())
    window.run_command("show_panel", {"panel": "output.nodeeval_panel"})
    return False

  # Output to a new file
  if output == 'new':
    active = False
    for tab in window.views():
      if 'Eval::Output' == tab.name(): active = tab
    if active: 
      _output_to_view(view, active, message, clear=clear)
      window.focus_view(active)
    else: 
      active = scratch(view, message, "Eval::Output", clear=clear)

    if syntax:
      active.settings().set('syntax', syntax)
    return False

  # Output to the current view/selection (work performed in the calling method)
  if output == 'replace':
    edit = view.begin_edit()
    view.replace(edit, region, message)
    view.end_edit(edit)
    return False

  if output == 'clipboard':
    sublime.set_clipboard( message )
    return False
  
  return False




#
# Helper to output views
#
def _output_to_view(v, output_file, output, clear=True):
  edit = output_file.begin_edit()
  if clear:
    region = sublime.Region(0, output_file.size())
    output_file.erase(edit, region)
  output_file.insert(edit, 0, output)
  output_file.end_edit(edit)

# 
# Helper to output a new Scratch (temp) file
# 
def scratch(v, output, title=False, **kwargs):
  scratch_file = v.window().new_file()
  if title:
    scratch_file.set_name(title)
  scratch_file.set_scratch(True)
  _output_to_view(v, scratch_file, output, **kwargs)
  scratch_file.set_read_only(False)

  return scratch_file


#
# Eval the "data" (message) with basically: `node -p -e data`
#
def eval(view, data, region, print_compile):
  global g_lastCwd
  # get the current working dir, if one exists...
  cwd = view.file_name()
  if cwd != None:
    cwd = os.path.dirname(cwd)
    g_lastCwd = cwd
  else:
    cwd = g_lastCwd

  plugin_settings = sublime.load_settings(settingsFilename)

  current_syntax = view.settings().get('syntax')

  file_engine = None
  for engine_name in plugin_settings.get('evals'):
    print engine_name
    engine = plugin_settings.get('evals').get(engine_name)
    if engine.get('syntax') in current_syntax:
      file_engine = engine
      break

  if file_engine == None:
    panel(view, "Cannot evaluate syntax %s." % current_syntax, False)
    return False

  command = [file_engine.get('command')] + file_engine.get('args')

  print "evaling syntax %s using %s in %s" % (current_syntax, ' '.join(command), cwd)

  try:
    # node = Popen([node_command, "-p", data.encode("utf-8")], stdout=PIPE, stderr=PIPE)
    if os.name == 'nt':
      node = Popen(command, cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    else:
      node = Popen(command, cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    node.stdin.write( data.encode("utf-8") )
    result, error = node.communicate()
  except OSError,e:
    error_message = """
 Please check that the absolute path to the node binary is correct:
 Attempting to execute: %s
 Error:
    """ % (command)
    print e
    panel(view, error_message, False)
    return False

  syntax = file_engine.get('outputSyntax')
  print syntax

  message = error if error else result
  panel(view, message, region, syntax)



#
# Get the selected text regions (or the whole document) and process it
#
class EvalEvalCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    # save the document size
    view_size = self.view.size()
    # get selections
    regions = self.view.sel()
    n_regions = list(regions)
    num = len(regions)
    x = len(self.view.substr(regions[0]))

    print_compile = False

    # select the whole document if there is no user selection
    if num <= 1 and x == 0:
      regions.clear()
      regions.add( sublime.Region(0, view_size) )

      print_compile = True

    # get current document encoding or set sane defaults
    encoding = self.view.encoding()
    if encoding == 'Undefined':
      encoding = 'utf-8'
    elif encoding == 'Western (Windows 1252)':
      encoding = 'windows-1252'

    # eval selections
    for region in regions:
      data = self.view.substr(region)
      eval(self.view, data, region, print_compile)

    regions.clear()
    regions.add(n_regions[0])

