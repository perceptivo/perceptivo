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