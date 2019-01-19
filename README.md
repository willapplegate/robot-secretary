# robot-secretary
Takes case numbers of civil suits in LA county and automatically creates key events in a specified google calendar.


Hi!

This is my first script. Apologies if it is inelegant, though I hope one can look past a grotesque machine so long as it
machines properly.

It pulls case numbers, separated by \n, from case_numbers_list.txt. It enters those numbers into LA County's case search,
currently found at (http://www.lacourt.org/casesummary/ui/). It pulls down the results page and saves an html copy of the
page. It parses the page, and looks for key dates and other information (FSC, OSC, Trial, caseNO, etc..).

Once parsing is complete, it queries a specified google calendar for events on the relevant date that include both the
name of the case and the relevant event (FSC, Trial, etc...). If if finds no such event, it creates such an event. If such
an event is found, but on an incorrect date, the event is moved to the correct day. If such an event is found on the correct
date, it passes.

There is machinery in place to allow for 'easy' creation of new dates, should one wish to extrapolate other important dates
from the parsed information - such as Jury Fee dates.

The master version does not handle errors in source material (i.e. if it cannot find any of the above dates in results page
from LAcourt. This is the next step.

A further step is to facilitate other users entering their own personal information for gcal integration.
