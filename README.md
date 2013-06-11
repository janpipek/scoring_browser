This program enables you to browse mesh data created in Geant4
using macro-based scoring (/score/...).

Features
--------
* 2D tables along any axes
* absolute vs. relative values
* colour background (white - red - black)
* export of 2D tables to CSV
* simple statistics display for cells
* reduction in any dimension if the data table is too detailed

Requirements
------------
* python (2.7 or 3.2)
* PyQt4
* numpy

Program has been tested on a Linux machine and on Windows (a while ago).
It should be platform-independent.

Usage
-----

    python main.pyw
    python main.pyw datafile

I believe that the DataMatrix class can be used on its own.

History
-------
11 Jun 2013 - Few changes that make the program easier to work with but no new features.

01 Feb 2012 - I had a scoring file which I had to visualize quickly its contents but there
	was no simple way how to do it. So I started with this project.
	
Contact
-------
I'd be happy to accept feature requests, cooperation, questions, bug reports...
Please write to jan.pipek AT gmail.com
