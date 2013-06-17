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

Turns out my little script is not used only by developers. So I split
my installation instruction into those aimed at (Python) developers and
those for everybody else.

Installation (developers)
-------------------------

Not much to it. Install dependency listed in ``requirements.txt``, clone
this repo (or just copy ``hoover_reader.py`` and that's it.

Installation (others)
---------------------

First some bad news. Successful export will probably not be directly useful or
usable to you. The good news is that your friendly neighbourhood programmer
should not have problems transforming into any shape you like. I also plan to
write one myself when I finally have some time again. Hopefully soon.

I have packed my script and uploaded it to http://markos.gaivo.net/greader.zip 
It works on my machine, hopefully yours too.

To use it, do following:

1. Download Python 2.7.5 if you use Windows (should already be installed on Mac)
   from http://www.python.org/download/ and run installer. By default it should
   install it in C:\Python2.7

2. Download above mentioned zipped script and unpack it anywhere you like.
   Let's say it is on C:\. This should create a sub-directory called
   greader that contains folders and a few files with .py at the end.

3. If step 1 was successful, then files with .py at the end should have
   a Python logo on them (on Windows). If they don't, then do let me know
   since next steps probably won't work.

4. Create settings.py file with lines::

    USERNAME = "your_username"
    PASSWORD = "your_password"
    BACKUP_DIRECTORY = "where_to_save_data"

your_username and your_password are username and password you use to connect
Google Reader. Maybe the easiest way to do it is to open settings.py.template
in greader directory with Notepad and save configured version as settings.py.

``BACKUP_DIRECTORY`` should list path to where you want to save your data.
Directory will be created if it does not exist yet, but it should conform to
platform specific format (so on Windows it should start with drive like C:
and followed with backslash-delimited path).

5. Double-click on hoover_reader.py should execute script and start backing
   up data into BACKUP_DIRECTORY. Check also `Usage` section.

*Note*: I tried my best, but I can't guarantee this script gets all of data
you stored. So to be on the safe side try also other approaches:

- .. _Amir's solution: http://markos.gaivo.net/blog/?p=1097#comment-312201
- .. _Knarf's solution: http://productforums.google.com/forum/#!msg/reader/BO3H81Nb68M/NLNwY2tJ1PMJ

Better to have a backup too many than one too few.


Usage
-----

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
- export to web pages (HTML)
- import script for Tiny Tiny RSS
- replace feedburner links with real addresses (to be safe when that service
  also gets cancelled)
- I would like to learn how to export Notes (you already can using tools
  provided by Google)
