#!/bin/bash
# generates po and mo files from the project source code

ARG=$1

print_help () {
	echo
	echo "Usage: $0 [-h|-mo|-po]"
	echo "    -h    Print this help message"
	echo "    -mo   Generate mo files and install them in the locale directory"
	echo "    -po   Generate new po files from the project source"
	echo
}

if [ "$ARG" = "-po" ]
then
    env python2.5 mki18n.py -pv --domain=Editra
    # Copy all .new files to override the originals
    for fname in $(ls); do
        if ! [ -z $(echo $fname | grep '.*\.new') ]; then
            name=$(echo $fname | sed 's/.new//')
            mv $fname $name
        fi
    done
elif [ "$ARG" = "-mo" ]
then
    env python2.5 mki18n.py -mv --domain=Editra --moTarget=../../locale
else
    print_help
fi    
