#!/bin/bash

sed -ri ':a;s/^( *)\t/\1    /;ta' $1
