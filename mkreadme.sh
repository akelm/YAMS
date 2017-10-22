#! /bin/bash
grip  README.md --export README.html
wkhtmltopdf README.html README.pdf
mv README.html README.pdf docs/