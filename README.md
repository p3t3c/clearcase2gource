clearcase2gource
================

Process the history from a clear case repository so that it can be rendered using Gource.

Gource can be found here: https://code.google.com/p/gource/

## Three Step approach

Step 1
------
Get the history out of clear case
   
    cleartool setview yourView
    cd /vob/location
    cleartool lshistory -all -fmt "Element: %n| Date: %d| User:%u| Operation: %e| Object:%[type]p| SimpleType: %m| OperationKind: %o\n" > cc_history
   
Step 2
------
Run this script

    tac cc_history | ./cc-gsource-conv.py  > gource.log
Uses tac instread of cat because the result of the lshistory comes out backward.

Step 3
------
    gource gource.log
You may want to customize the gource parameters.
