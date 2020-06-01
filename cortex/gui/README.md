# The website

It is half baked. I am really sorry for this.

I will not make excuses for it.

###Known issues:
* Snapshot view is undercooked. I ran out of time trying to find solutions to the next bullet
* BSON does not work, and other heatmap solutions behaved poorly, thus there is view of the Depth Image
* Back button (when exists) takes you back to root.
* Color scheme for the locations over time is a bit weird, couldn't find switch to make it not repeating and become hotter as time progresses.
* No package managment. I set out to build something really light-weight, only to discover 75% of the way in, that a LOT of things don't work without package management.


### Good bits:
* There is a system that accepts snapshot data, requests the data for it, then passes it to their registered handler, which puts html in the docuemnt
    * This means that to add new data-types, you need to write a handler, and add it's topic to a map, and you're done.
* There is a website running when you run the system, which is something I was afraid would not happen.



