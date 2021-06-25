# Software Overview

## Block Diagram

```{eval-rst}
.. graphviz::

    digraph g {
        newrank=true
        fontname="Courier New"
        graph [fontsize=30 splines=true overlap=false rankdir = "TB"];
        ratio = auto;
      
        
        subgraph cluster_cpu0{
            label="CPU0"
            cpu0 [label="Messenger\ncpu0" shape="box" width=3]
            gui [label="GUI"]
            io [label="I/O"]
        }
        
        subgraph cluster_pi0 {
            label="Raspi0"
            
            pi0 [label="Messenger\nraspi0" shape="box" width=3]
            manager [label="Session Manager"]
                psycho [label="Psychoacoustic Model"]
                pupil [label="Pupil Extraction"]
                stim [label="Stimulus Manager"]
            subgraph cluster_pi0_p1{
                label="p1"
                picam [label="PiCamera"]
            }
            
                
            subgraph cluster_pi0_p2{
                label="p2"
                
                sound [label="Sound Server"]
            }
        }
        
        subgraph cluster_pi1{
            label="Raspi1"
            pi1 [label="Messenger\nraspi1" shape="box" width=3]
            visman [label="Visual Manager"]
            frameserve [label="Frameserver"]
        }
        
        
        {rank=same; pi0 pi1 cpu0}
        
        cpu0 -> pi0 [label="control"]
        pi0 -> cpu0 [label="data"]
        pi0 -> pi1 [label="control"]
        pi1 -> pi0 [label="data"]
        
        
        cpu0 -> gui [label="data"]
        gui -> cpu0 [label="control"]
        cpu0 -> io [label="data"]
        
        pi0 -> manager [label="control"]
        manager -> pi0 [label="data"]
        manager -> sound
        manager -> picam
        psycho -> manager
        psycho -> stim
        stim -> sound
        picam -> pupil
        picam -> manager
        pupil -> psycho
        pupil -> manager
        stim -> manager
        {rank=same; sound picam}
        
        pi1 -> visman
        visman -> pi1
        visman -> frameserve
    
        
    }
```

## Draft Description

### Message-based architecture

- The system will consist of separable modules that communicate with a globally-defined enum of message types. 
- The system will consist of independent computers networked with an \[ad-hoc or hosted? wireless network\].
- Messages will be serialized and sent as tcp packets between computers, and as inter-and intra-process packets within a computer.

### Distribution of Labor

- One computer will serve as the clinician-facing interface that controls the operation of the examination
- One computer will serve as the primary examination device, delivering auditory stimuli, measuring pupil dilation, and controlling the stepping algorithm
- One computer will serve as the patient-facing interface, presenting visual stimuli (as well as physical enclosure for cameras and speakers)

### Synchronization

- The two computers operating the examination will be tightly synchronized with a shared real-time clock
- The examination computers will communicate asynchronously with the clinician-facing computer

### GUI

- The GUI will be made with Qt6, written in PySide6
- \[*control requirements*\]
- \[*display requirements*\]
- \[*utility requirements*\]

### Image Capture

- Pupil images will be captured with a PiCam NoIR camera as single-channel luminance images from a YUV-encoded frame
- Raw images will only be saved if explicitly requested, otherwise they will be shown in the GUI as a diagnostic

### Pupil Processing

- Pupil diameter will be extracted as the shorter diameter of an ellipse fit on the edges of a tracked pupil to account for eccentricity/occlusion
- \[*filtering and signal conditioning*\]
- \[*preservation of provenance*\]

### Psychoacoustic Model

this'll be a bit of work, ya!?

### Sound

#### Generation

talk to avinash about stimuli

#### Presentation

- Sound will be presented with jack audio
- Sound will be prebuffered in the presenting process, prioritizing continuity over low-latency

#### Recording & Calibration

### Video

#### Generation

#### Presentation

### Patient Data

### Maintenance, Logging, Debugging