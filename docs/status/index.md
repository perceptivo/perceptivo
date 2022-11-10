# Project Status

High-level overview of Perceptivo's status.

```{admonition} Last Updated
November 2022
```

See also:

* [Roadmap](roadmap.md) for high-level development plan and milestones
* [TODO](todo.md) for more specific lower-level requirements.

```{toctree}
---
maxdepth: 2
hidden: true
---
roadmap
todo
```

## Software

See the [Software Overview](../software/overview.md) for a description of how
the package is designed.

The structure of the software has been largely completed such that all the 
remaining pieces should have some relatively clear place to go and defined
way of interacting with the existing components. The remaining work can be roughly
put in three groups:

### Patient Runtime

The patient loop is in a
runnable state, and has baseline implementations of all its major components:
sound synthesis & output, video capture, pupil extraction, and audiogram 
estimation. This is where most of the development time has been spent
to-date. All could use some optimization, particularly the video capture and
pupil extraction systems, which need probably significant performance optimization.
The visual stimuli to keep attention are also not implemented yet, but that
should be relatively straightforward to do in psychopy or similar. That might
need to be written as a third runtime, depending on the perf that can be
squeezed out of the pi. If all else fails, effectively all of this code except
the specific usage of the picamera can be trivially ported to more powerful hardware.

### Clinician Runtime

The clinician runtime is the means by which
the clinician administers the exam and manages patient data. Currently
it has a *very* rough GUI in place, with points of extension for future
work, but beyond that needs to have most of its functionality implemented.
This should be done keeping Qt's signal/slot architecture in mind, as 
its pretty compatible with the message-passing style intended to be used
in the rest of the system. So signals/slots need to be be made that match the
configuration and use of the patient runtime, and then hooked up with the
networking modules. 

### Integration

The last bit of work before user testing and finishing the industrial design
will be on system integration: getting the two (potentially three) runtimes to 
work together. The only really synchronization-critical part of the system is
between the sound output and the image acquisition, but even that can be somewhat
asynchronous as long as the time of acquisition is known and comparable to the
time of audio presentation. The rest of the system can be asynchronous up to the
allowance of UX - eg. depending on streaming latencies that are tolerable in the
clinician GUI. The package is written in python as a prototype, so performance
optimization might require some of those components be rewritten in a compiled
language to make smooth. 

The actual work of integration will consist of hooking up the methods
of the various runtimes to networking objects, operationalized by sockets, 
each of the runtimes having several depending on the independent components.
Within a runtime (ie. on the same computer) IPC can be used so that the 
components can be made to run independently (eg. as different processes),
and between runtimes TCP is good for commands and UDP is good for streaming. That
should all be configurable in the {py:class}`~perceptivo.types.networking.Socket` class,
which is consumed by {py:class}`~perceptivo.networking.node.Node`.

Afterwards, in order to make the product marketable, more work will be needed
to polish it, finish the industrial design, branding, etc. but the above
steps should make it at least functional.

```{warning}
Special care will need to be taken to make sure that the open source licenses
of the projects used within are respected - specifically any projects that use
strong copyleft licenses like GPL-3.0 - if the end-product will be distributed
in a proprietary way. Please note that python is very difficult to distribute
in a way that's hard to reverse engineer, and so it would be trivial
for someone to dump the contents of the raspi flash drive to see the source.

Rather than distribute it in a proprietary way, I would consider keeping the 
source open and patenting it for commercial use (eg. other people can use and inspect
the source, just not for commercial purposes).
```

## Hardware

The hardware has been specified on a draft level, and some initial usability testing
was done with the picamera to make sure it worked with a raspiOS update (buster)
that happened during primary development, but much of the rest of the hardware 
remains to be designed and built.


