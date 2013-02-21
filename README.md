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
