#! /bin/bash

if [[ $# == 0 || $1 == "-h" || $1 == "--help" ]]; then
  cat <<-EoF
Create a PDF, borderless at the sides, from panoramic images.
Usage: $0 {PDF} {options for borderlessPanoramas.py} images...
where:
{PDF}
  is the output PDF file name; and
{options for borderlessPanoramas.py}
  are options such as --pageSize=A3+ passed to borderlessPanoramas.py, which must not include --output because this script sets that.

Here are the options for borderlessPanoramas.py:
EoF
  borderlessPanoramas.py --help
  exit 0
fi

tmp=borderlessPanoramas-$$.ps
trap '{ rm -f -- $tmp; }' EXIT
out="$1"
shift
borderlessPanoramas.py --output=$tmp "$@"
gs -dNOSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile="$out" $tmp >/dev/null