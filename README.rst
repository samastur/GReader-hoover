==============
GReader-hoover
==============

A dirty python script for exporting information from Google Reader that
mostly can not be exported using Google's tools (like your tagged items).

I did not spend time polishing script that will not be useful for long
(and don't intend to do so), but please do let me know if there is
anything else you would like to see exported that isn't yet.

Installation & usage
====================

Not much to it. Install dependency listed in ``requirements.txt``, clone
this repo (or just copy ``hoover_reader.py`` and that's it.

You can run it with default settings by proving username and password on
command line like::

    python hoover_reader.py <your_username> <your_password>

If you want to have more control over your backup, then rename
``settings.py.template`` to ``settings.py`` and edit configuration options
to your liking. Hopefully their purpose is obvious, but please ask if it
isn't. If you include username and password, then you don't need to
specify it on CLI::

    python hoover_reader.py

*Note*: Username does not include domain name part of your username unless
it is different than Google's.

Also, if you are using 2-step verification (which you should), then you
need to create a special password on your Google account page (found in
security part of your account where you manage access from applications
and web sites). You can delete it once you are done with backup.


TODO
====
- replace feedburner links with real addresses (to be safe when that one
  also gets cancelled)
- I would like to learn how to export Notes (you already can using tools
  provided by Google)
