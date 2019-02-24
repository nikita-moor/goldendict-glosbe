# glosbe-wrapper
Python script to use Glosbe.com in GoldenDict


# How to use

Open GoldenDict, go to the menu Edit|Dictionaries|Programs and add new record:

* type: html
* name: (on your choice)
* command: ~/work/glosbe.py --from=pol --to=eng %GDWORD%
* icon: ~/work/glosbe.png

Use ISO 693-3 three letter language code:
* https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
* http://www-01.sil.org/iso639-3/codes.asp


# Comments

The script uses official Glosbe RESTful API and caches requests.
