#!/bin/bash

sudo apt-get -y install build-essential fabric libevent1-dev libmemcached-dev python-pip python2.7-dev
sudo pip install virtualenv

virtualenv ENV
source ENV/bin/activate
ORIGPATH=$PATH
export PATH=$PWD/ENV/bin:$PATH
pip install -r requirements.txt
deactivate
export PATH=$ORIGPATH
