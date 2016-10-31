#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Glosbe dictionary for GoldenDict using RESTful API
#
# How to use:
# ./glosbe.py --from=pol --to=eng trzymać
#
# Parameters:
# from, to - ISO 693-3 three letter language code


CACHE_DIR = ""


import sys, os, re
import getopt
import requests

reload(sys)  
sys.setdefaultencoding('utf8')


def usage():
    print("Glosbe dictionary\nHere should be man pages...")


def load_from_web(lang_from, lang_dest, phrase):
    """
    from - (required) language of phrase to translate, values: ISO 693-3 three letter language code, no default, beware: if language is invalid you'll get server 500 error code in return
    dest - (required) destination language, values: ISO 693-3 three letter language code, no default
    phrase - (required) phrase to be translated, values: arbitrary text, no default, case sensitive
    tm - whether to include examples (make translation memories search), values: 'true' or 'false', default: 'false'
    format - described elsewhere

    Example:
    https://glosbe.com/gapi/translate?from=pol&dest=eng&format=json&phrase=trzyma%C5%82&pretty=true&tm=false
    """

    r_url = 'https://glosbe.com/gapi/translate'
    r_params = {
        'from'  : lang_from,
        'dest'  : lang_dest,
        'phrase': phrase,
        'tm'    : 'true',
        'format': 'json'
    }
    r = requests.get(r_url, params = r_params)
    if r.status_code != 200:
        print("Error: Server returned status code {}".format(r.status_code))
        sys.exit(2)
    return r.json()


def load_suggest(lang_from, lang_dest, phrase):
    """
    from - (required) language of phrase to translate, values: ISO 693-3 three letter language code, no default, beware: if language is invalid you'll get server 500 error code in return
    dest - (required) destination language, values: ISO 693-3 three letter language code, no default
    phrase - (required) phrase to be translated, values: arbitrary text, no default, case sensitive
    format - described elsewhere

    Example:
    https://ru.glosbe.com/ajax/phrasesAutosuggest?from=pl&dest=ru&phrase=trzyma%C5%82
    """

    r_url = 'https://ru.glosbe.com/ajax/phrasesAutosuggest'
    r_params = {
        'from'  : lang_from,
        'dest'  : lang_dest,
        'phrase': phrase,
        'format': 'json'
    }
    r = requests.get(r_url, params = r_params)
    if r.status_code != 200:
        print("Error: Server returned status code {}".format(r.status_code))
        sys.exit(2)
    return r.json()


def parse_web(title, data):
    dictionary = ""
    for rec in data["tuc"]:
        for key, value in rec.iteritems():
            if key == "phrase":
                s = "<dt>{p[text]}</dt>".format(p=value)
                dictionary += "\n" + s
            elif key == "meanings":
                for v in value:
                    s = "<dd><a class='glosbe-lang'>({p[language]})</a> {p[text]}</dd>".format(p=v)
                    dictionary += "\n" + s
    if len(dictionary) > 0:
        dictionary = "<dl class='glosbe-list'>{}\n</dl>".format(dictionary)

    examples = ""
    for rec in data["examples"]:
        s = "<dt>{p[first]}</dt>".format(p=rec)
        s += "<dd>{p[second]}</dd>".format(p=rec)
        examples += "\n" + s
    if len(examples) > 0:
        examples = "<div class='dsl_headwords'><p>Example sentences:</p></div>\n<dl class='glosbe-examples'>{}\n</dl>".format(examples)
    examples = re.sub('class="keyword"', 'class="glosbe-keyword"', examples)

    html = """<span class='dsl_article'>
  <div class='dsl_headwords'><p>{}</p></div>
  <div class='dsl_definition'>
{}
{}
  </div>
</span>""".format(title, dictionary, examples)
    return html


def main(argv):

    # init -----------------------------------------------------------------
    work_dir = os.path.dirname(os.path.realpath(__file__))
    if len(CACHE_DIR) > 0:
        cache_dir = CACHE_DIR
        if cache_dir[-1] != "/":
            cache_dir = cache_dir + "/"
    else:
        cache_dir = work_dir + "/cache/"
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    # read arg -------------------------------------------------------------
    lang_from = "pol"
    lang_dest = "eng"
    text = ""

    try:
        opts, args = getopt.getopt(argv, "h", ["help", "from=", "to="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit(2)
        elif opt == "--from":
            lang_from = arg
        elif opt == "--to":
            lang_dest = arg

    text = "".join(args).lower()

    if len(text) == 0:
        usage()
        sys.exit(2)

    # load dict ------------------------------------------------------------
    file_name = "{}[{}-{}] {}.html".format(cache_dir, lang_from, lang_dest, text)
    if not os.path.isfile(file_name):
        data = load_from_web(lang_from, lang_dest, text)
        if len(data["tuc"]) > 0 or len(data["examples"]) > 0:
            html_dict = parse_web(text, data)
        else:
            """ We can try to load suggestion from Glosbe, but IRL it's useless """
            #data = load_suggest(lang_from, lang_dest, text)
            #html_dict = ', '.join(data)
            #print(html_dict)
            sys.exit(0)
        f = open(file_name, "w")
        f.write(html_dict)
        f.close()
    else:
        f = open(file_name, "r")
        html_dict = f.read()
        f.close()

    # html document --------------------------------------------------------
    f = open(work_dir + "/glosbe.css", "r")
    css = f.read()
    f.close()

    html = """
<html>
  <head>
    <meta charset='utf-8'/>
    <style media="screen" type="text/css">
{}
    </style>
  </head>
  <body>
{}
  </body>
</html>
""".format(css, html_dict)
    print(html)


if __name__ == "__main__":
    main(sys.argv[1:])
