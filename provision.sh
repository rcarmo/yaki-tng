#!/bin/bash

. /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv yaki
workon yaki
pip install -r /vagrant/requirements.txt
