#!/bin/bash

kwdumpwork --input $1:dump --select-tuples Url,SelectionRanks --output $2:dump
