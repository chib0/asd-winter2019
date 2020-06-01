[![Build Status](https://travis-ci.com/chib0/asd-winter2019.svg?branch=master)](https://travis-ci.com/chib0/asd-winter2019)
[![Coverage](https://codecov.io/gh/chib0/asd-winter2019/branch/master/graph/badge.svg)](https://github.com/chib0/asd-winter2019)

# All Your Thoughts Are Belong To Us
This is a project for the Advanced System Design Course of TAU / Winter '19-'20.
It's a not-too-big client-server app that teaches and showcases how to use different CI/CD tools as well as good software design patterns

I'll try to keep the code documented (as well as self documenting) while doing my best to explain design choices.

# Contents
- cortex - a python package implementing a clinet-server apo that communicates and stores messages(thoughts), a server then aggregates them, as well as implements a web-server that allows access to said messages(thoughts)

    #####Runnables:
    - /client - contains image file reader, arbitrator, and client implementattion
    - /core - Core objects of the project
    - /api - Implements the rest api that allows querying information from the server 
    - /cli - Implements a command line interface that allows basic querying of the api
    - /server - cli and server choice implementations.
    - /web - the webserver implementation
    #####Other
    - /utils - a utitlity package, mainly filesystems, general parsers/encoders, database implementations, dispatchers, etc.

#Installation

####package installation
running `/scripts/install.sh` will install the package on the current system, requiring only python and virtualenv to be installed.

####dockerizing

running `scripts/make-dockers` will create dockers for the systems.

#### Running
`/scripts/run-pipeline.sh` will run the pipeline after the dockers have been created.


# Usage
For each runnable, see readme in every cortex/\<Runnable\>

# Design Guidelines
The main point for me in this project is Interchangeability and Pipelines.
Look for readmes in every module or documentation in the files for more information.

## Interchangeability
Every python component in the project should be easily interchangeable.
This is achieved using a Repository/ModuleGatherer object that finds and returns the correct object to handle uri's and data
There are, of course, constraints on the dispatchers, Database adapters, etc, but they should be well documented.

Repositories are automatically constructed using Aspect Oriented programming, allowing thorough configuration for property and module collection.
Having said that, repositories can also be manually implemented, as in the case of the dispatcher repository.

## Aspect Oriented Programming
The repository works a lot as pytest does, collecting functions, inferring their targets, and creating records for them.
This allows the data pipeline to register these functions easily, with their target as topics, for the message queue.

## Message Queue and Data Pipeline
While the current project uses RabbitMQ, it is extremely easy to replace that with any other message queue, and all that is 
required is to implement a run and stop function, as well as handler registration.

The pipeline is implemented using the Tee object, which allows binding a function to consume a topic, then publising its results to another.

Every part of the pipeline accepts a encoders and decoders for the output and input respectively, for easy changing of the transport.

 



# Conclusion
I hope you had fun, hope you liked what you saw, reach out if you have any questions ( looking at you, whoever grades this, and also you, kind stranger that has stumbled across this somehow )
