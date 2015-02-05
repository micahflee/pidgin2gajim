pidgin2gajim
============

This program converts OTR keys from Pidgin format to Gajim format.

Your Pidgin OTR files are here:

    ~/.purple/otr.private_key  # secret key
    ~/.purple/otr.fingerprints # fingerprints

Your Gajim OTR files are here:

    ~/.local/share/gajim/ACCOUNT.key3 # secret key
    ~/.local/share/gajim/ACCOUNT.fpr  # fingerprints

When you run pidgin2gajim.py, it automatically loads your Pidgin OTR files from ~/.purple/. Then it creates a new directory relative to your current path called output and saves Gajim-formatted .key3 and .fpr files into it for each Pidgin account you have.

You then have to manually copy the .key3 and .fpr files from the output directory into ~/.local/share/gajim/.

I copied a bunch of code from Guardian Project's otrfileconverter project to load and parse the Pidgin OTR private key file: https://github.com/guardianproject/otrfileconverter

How to Use
----------

First install Gajim:

    sudo apt-get install gajim

Run it and set up your jabber accounts. Click Edit, Plugins, switch to the Available tab, and download and install the Off-the-Record plugin. On the Plugins window, click Configure while Off-the-Record is selected to open the OTR plugin settings. For each jabber account, generate a new OTR key (just to create filenames that we'll overwrite). When you have done this, completely exit Gajim.

Then download and run pidgin2gajim:

    git clone https://github.com/micahflee/pidgin2gajim.git
    cd pidgin2gajim
    virtualenv env  # needs python-virtualenv 
    . env/bin/activate
    pip install pyparsing
    pip install python-potr
    ./pidgin2gajim.py
    ls -l output
    deactivate

Then overwrite your Gajim OTR keys with the ones that were just created in the output directory. Something like:

    cp output/micah@jabber.ccc.de.key3 ~/.local/share/gajim/jabber.ccc.de.key3
    cp output/micah@jabber.ccc.de.fpr ~/.local/share/gajim/jabber.ccc.de.fpr

Now open Gajim again. If all went well, you should now have your Pidgin OTR keys in Gajim.

There is a known bug where Gajim sometimes crashes the first time it tries to parse your saved fingerprints: https://github.com/micahflee/pidgin2gajim/issues/1

If this happens, you can just run Gajim again and it should work fine. You'll just be missing a couple of fingerprints from people you're talked to. Your actual secret key should be exactly the same and have the same fingerprint.
