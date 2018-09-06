#!/bin/bash

while true; do
	python3 mainScrape.py
	killall chrome
done