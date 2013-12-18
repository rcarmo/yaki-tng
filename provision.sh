#!/bin/bash

# Provisioning script helper for Vagrant -- this sets up the virtualenv you should use for development (and deployment)

. /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv yaki
workon yaki
pip install -r /vagrant/requirements.txt
