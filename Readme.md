Eval Sublime Text 2 Package
===============================

Fork of NodeEval, with hacked on support for CoffeeScript and F#. Adding other languages should be relatively easy - as long as their compilers/interpreters support running from stdin.

Install
-------
To install, clone the repo to Packages folder of Sublime Text 2.

Go to:

on Windows: 

    %APPDATA%\Sublime Text 2\Packages

on Ubuntu (and other others? no idea):

    ~/.config/sublime-text-2/Packages  

and then:

    git clone https://github.com/zapu/SublimeText-Evals.git Evals

Usage
-----
After installation, create your settings file (Preferences > Package Settings > Evals > Settings - User). Just copy everything from default settings file and change paths.

Then, when editing JavaScript, CoffeeScript or F#, press `ctrl+shift+l` to evaluate and display results. Files do not have to be saved, but their syntax has to be set properly. Use `ctrl+p` and `Set Syntax: ...`.

By default, CoffeeScript is set to compile to JavaScript, rather than to evaluate the code. My workflow is to use `ctrl+shift+l` twice when I need to run CoffeeScript code.
  - Pressed the first time, it will output the JavaScript.
  - Pressed the second time, it will run that JavaScript.

Unsure if this works with ST3, probably not. 

Patches are welcome. You can, for example, pull the new threading code from upstream.


Author & Contributors
----------------------
[Derek Anderson](http://twitter.com/derekanderson)

[Michał Zochniak](github.com/zapu)

License
-------
MIT License