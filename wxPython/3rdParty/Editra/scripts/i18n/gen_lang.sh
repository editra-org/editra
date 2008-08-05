#!/bin/bash
##############################################################################
# Generates po and mo files from the project source code
# Author: Cody Precord
# Copyright: Cody Precord <cprecord@editra.org>
# License: wxWindows
##############################################################################

##############################################################################
# Variables
##############################################################################
ARG=$1

##############################################################################
# Function: print_help
# Purpose: Print the scripts usage help to the console
##############################################################################
print_help () {
	echo
	echo "Usage: $0 [-h|-mo|-po|-all]"
	echo "    -h    Print this help message"
	echo "    -mo   Generate mo files and install them in the locale directory"
	echo "    -po   Generate new po files from the project source"
    echo "    -all  Regenerate everything"
	echo
}

##############################################################################
# Function: gen_po
# Purpose: Generate new po files from the source
##############################################################################
gen_po () {
    env python2.5 mki18n.py -pv --domain=Editra
    # Copy all .new files to override the originals
    for fname in $(ls); do
        if ! [ -z $(echo $fname | grep '.*\.new') ]; then
            name=$(echo $fname | sed 's/.new//')
            mv $fname $name
        fi
    done
}

##############################################################################
# Function: make_mo
# Purpose: Make mo files and place them in the appropriate locale directory
##############################################################################
make_mo () {
    env python2.5 mki18n.py -mv --domain=Editra --moTarget=../../locale
}


##############################################################################
# Main
##############################################################################

if [ "$ARG" = "-po" ]
then
    gen_po
elif [ "$ARG" = "-mo" ]
then
    make_mo
elif [ "$ARG" = "-all" ]
then
    gen_po
    make_mo
else
    print_help
fi    
