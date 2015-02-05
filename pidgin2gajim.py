#!/usr/bin/env python
"""
Locate existing libpurple (pidgin) otr private keys and fingerprints and
convert them to gajim format.

Note:
You have to manually copy the .key3 and .fpr files from the output directory
into ~/.local/share/gajim/.
"""

import os
from base64 import b64decode

from pyparsing import *
from potr.utils import bytes_to_long
from potr.compatcrypto import DSAKey

# much of this is copied and pasted from:
# https://github.com/guardianproject/otrfileconverter 

def verifyLen(t):
    t = t[0]
    if t.len is not None:
        t1len = len(t[1])
        if t1len != t.len:
            raise ParseFatalException(
                "invalid data of length %d, expected %s" % (t1len, t.len))
    return t[1]


def parse_sexp(data):
    """parse sexp/S-expression format and return a python list"""
    # define punctuation literals
    LPAR, RPAR, LBRK, RBRK, LBRC, RBRC, VBAR = map(Suppress, "()[]{}|")

    decimal = Word("123456789", nums).setParseAction(lambda t: int(t[0]))
    bytes = Word(printables)
    raw = Group(decimal.setResultsName("len") + Suppress(":") + bytes).setParseAction(verifyLen)
    token = Word(alphanums + "-./_:*+=")
    base64_ = Group(Optional(decimal, default=None).setResultsName("len") + VBAR
                    + OneOrMore(Word(alphanums + "+/=")).setParseAction(lambda t: b64decode("".join(t)))
                    + VBAR).setParseAction(verifyLen)

    hexadecimal = ("#" + OneOrMore(Word(hexnums)) + "#") \
        .setParseAction(lambda t: int("".join(t[1:-1]), 16))
    qString = Group(Optional(decimal, default=None).setResultsName("len") +
                    dblQuotedString.setParseAction(removeQuotes)).setParseAction(verifyLen)
    simpleString = raw | token | base64_ | hexadecimal | qString

    display = LBRK + simpleString + RBRK
    string_ = Optional(display) + simpleString

    sexp = Forward()
    sexpList = Group(LPAR + ZeroOrMore(sexp) + RPAR)
    sexp << ( string_ | sexpList )

    try:
        sexpr = sexp.parseString(data)
        return sexpr.asList()[0][1:]
    except ParseFatalException as pfe:
        print "Error:", pfe.msg
        print line(pfe.loc, data)
        print pfe.markInputline()


def parse(filename):
    """parse the otr.private_key S-Expression and return an OTR dict"""

    with open(filename, 'r') as f:
        data = ''.join(line for line in f.readlines())

    sexplist = parse_sexp(data)
    keydict = dict()
    for sexpkey in sexplist:
        if sexpkey[0] == "account":
            key = dict()
            name = ''
            for element in sexpkey:
                # 'name' must be the first element in the sexp or BOOM!
                if element[0] == "name":
                    if element[1].find('/') > -1:
                        name, resource = element[1].split('/')
                    else:
                        name = element[1].strip()
                        resource = ''
                    key = dict()
                    key['name'] = name.strip()
                    key['resource'] = resource.strip()
                if element[0] == "protocol":
                    key['protocol'] = element[1]
                elif element[0] == "private-key":
                    if element[1][0] == 'dsa':
                        key['type'] = 'dsa'
                        for num in element[1][1:6]:
                            key[num[0]] = num[1]
            keytuple = (key['y'], key['g'], key['p'], key['q'], key['x'])
            key['dsakey'] = DSAKey(keytuple, private=True)
            key['fingerprint'] = '{0:040x}'.format(bytes_to_long(key['dsakey'].fingerprint()))
            keydict[name] = key
    return keydict


if __name__ == "__main__":
    home_dir = os.getenv('HOME')
    pidgin_key_filename =  os.path.join(home_dir, '.purple', 'otr.private_key')
    pidgin_fp_filename = os.path.join(home_dir, '.purple', 'otr.fingerprints')

    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    keys = parse(pidgin_key_filename)

    gajim_fps = dict()
    for account in keys:
        gajim_fps[account] = ''

    with open(pidgin_fp_filename, 'r') as f:
        pidgin_fps = [x.split() for x in f]
    for fp in pidgin_fps:
        if fp[2] == 'prpl-jabber':
            if len(fp) < 5:
                fp.append('')
            fp[1] = fp[1].split('/')[0]
            fp[2] = 'xmpp'
            gajim_fps[fp[1]] += '\t'.join(fp) + '\n'

    for account in keys:
        serialized_private_key = keys[account]['dsakey'].serializePrivateKey()
        with open(os.path.join(output_dir, '%s.key3' % account), 'w') as f:
            f.write(serialized_private_key)
        with open(os.path.join(output_dir, '%s.fpr' % account), 'w') as f:
            f.write(gajim_fps[account])
