[![Build Status](https://travis-ci.com/chib0/asd-winter2019.svg?branch=master)](https://travis-ci.com/chib0/asd-winter2019)
[![Coverage](https://codecov.io/gh/chib0/asd-winter2019/branch/master/graph/badge.svg)](https://github.com/chib0/asd-winter2019)

# All Your Thoughts Are Belong To Us
This is a project for the Advanced System Design Course of TAU / Winter '19-'20.
It's a not-too-big client-server app that teaches and showcases how to use different CI/CD tools as well as good software design patterns

I'll try to keep the code documented (as well as self documenting) while doing my best to explain design choices.

# Contents
- cortex - a python package implementing a clinet-server apo that communicates and stores messages(thoughts), a server then aggregates them, as well as implements a web-server that allows access to said messages(thoughts)

	- /utils - a utitlity package that contains all non business logic stuff, or any stuff that could be reused in other systems.
    - /client - the client implementation.
    - /core - the server, parsers, db, and more implementations.    
    - /web - the webserver implementation  
   
# Usage
 ' TODO '

# Design Guidelines
## The Data Model
The main issue I had going into this was making the data model as detached as possible from the implementation.
Let's introduce the "Thought" class a the container that holds everything there is about a users thought.
This class is what is bounced between the client and the server and is displayed on the web-server.
It has some identifiers, like the user_id who thought it, the timestamp it was thought at ('metadata') and then it has actual snapshot data.

On the one hand, I didn't want the Thought class to have to change whenever fields are added to the server.
This meant I didn't want to expose the snapshot.<field> explicitly (i.e as a property).
On the other hand, that meant that the snapshot part of the Thought had to be rigid, or older parsers would have to be 
updated along with the data model, which generally doesn't happen.

As I consider the data-model itself rather rigid, having mostly additions and little removals, I believe a Thought
that is a very loose wrapper that exposes the metadata and snapshot the correct way to go.

This in turn means that the data model is defined by the snapshot and the metadata structures, 
and that the parsers are to expect data to be there. This is fine by me because the parsers are tightly coupled to the 
data model in terms of what is there.



# Conclusion
I hope you had fun, hope you liked what you saw, reach out if you have any questions ( looking at you, whoever grades this, and also you, kind stranger that has stumbled across this somehow )
