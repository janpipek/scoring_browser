This program enables you to browse data created in Geant4
using macro-based scoring (/score/...). It allows you to view
a table of data sliced along any of the axes (with the possibility
of absolute or relative value display with colourful background).

The program is at the beginning of development

Requirements
------------
* python (2.7 or 3.2)
* PyQt4
* numpy

Program has been tested on a Linux machine. However, no specific
Unix features were used, so it should be multi-platform.

Usage
-----

    python main.py
    python main.py datafile

I believe that the DataMatrix class can be used on its own.

History
-------
01/02/2012 - I had a scoring file which I had to visualize quickly its contents but there
	was no simple way how to do it. So I started with this project.
	
Contact
-------
I'd be happy to accept feature requests, cooperation, questions, bug reports...
Please write to jan.pipek AT gmail.com
