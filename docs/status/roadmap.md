# Roadmap

High-level overview of phases of development. Specific code-level TODO items should be
put in [TODO](todo.md)

## Completed

- [x] `2021-06-30` - **Design Draft** - Initial system diagrams for hardware and software 
- [x] `2021-08-09` - **Software Scaffold** - Structure of package
- [x] `2021-08-23` - **GUI Draft** - Initial visual draft of GUI
- [x] `2021-08-27` - **Networking Architecture** - Draft of socket types and distribution among patient and clinicial classes
- [x] `2021-10-20` - **Gammatone Synthesis**
- [x] `2021-11-08` - **Audiogram Estimation** - Algorithm to estimate audiogram from minimal number of samples
- [x] `2021-12-15` - **Patient Loop Structure** - A full draft of the structure of the patient processing loop 
- [x] `2022-01-05` - **Audio Output** - using Soundcard library
- [x] `2022-02-16` - **Pupil Extraction** - Implementation of a simplistic pupil extraction system using traditional image processing
- [x] `2022-02-28` - **Patient Loop Integration** - Integration of components into a running patient loop 

## Remaining

- [ ] **Refine Pupil Extraction** - The existing pupil extraction is very basic, this will need to get refined and made customizable by the clinician
- [ ] **Perf in Patient Loop** - The patient loop has been written and has a modular structure, but none of its components have been optimized for performance.
- [ ] **Networking** - A shell structure for networking components using sockets and message types has been written, but the communication between runtimes needs to be written and hooked up to the relevant actions
- [ ] **Visual Stimuli** - The stimuli used to keep the patient's attention are unimplemented
- [ ] **Hardware Design** - The hardware design has been drafted and parts picked, but much of the work on the hardware remains: testing, calibrating, and packaging
- [ ] **UX/UI** - The GUI is, at the moment, an extremely gestural shell, and so the UX/UI will need to be completed and user tested
- [ ] **Validation** - Everything needs to be validated with a patient! Including audiogram estimation, sound output, etc.
