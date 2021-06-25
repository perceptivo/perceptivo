# Overview

# Hardware Block Diagram

```{eval-rst}
.. graphviz::

    digraph g {
      newrank=true
      fontname="Courier New"
      graph [fontsize=30 splines=true overlap=false rankdir = "LR"];
      ratio = auto;
      
      subgraph cluster_booth{
          label="Booth"
          subgraph cluster_raspi0 {
              label="Raspi 0"
              "raspi0" [fontname = "Courier New" shape = "Mrecord" label ="Raspi 0\n+sd card" height=3];
              "dacadc"  [fontname = "Courier New" shape = "Mrecord"  label ="HifiBerry\n DAC+ADC Pro" height=2];
              "aamp60"  [fontname = "Courier New" shape = "Mrecord" label ="HiFiBerry\nAAmp60" height=1 ];
              "speaker_l"  [fontname = "Courier New" shape = "Mrecord" label ="Speaker (L)" ];
              "speaker_r"  [fontname = "Courier New" shape = "Mrecord" label ="Speaker (R)" ];
              "microphone"  [ fontname = "Courier New" shape = "Mrecord" label ="Microphone" ];
              "noir" [ fontname = "Courier New" shape = "Mrecord" label ="NoIR Camera" ];
              "psu" [shape = "Mrecord" label="18V 2.6A PSU"]
            {rank=same; noir dacadc}
            {rank=same; aamp60 microphone}
            {rank=same; speaker_l speaker_r psu}
          }
          dacadc -> raspi0 [label="microphone input"]
          dacadc -> raspi0 [label="power"]
          raspi0 -> dacadc [label="sound output"];
          dacadc -> aamp60 [label="sound output"];
          aamp60 -> dacadc [label="power"];
          microphone -> dacadc
          aamp60 -> speaker_l
          aamp60 -> speaker_r
          psu -> aamp60 [label="power"]
          noir -> raspi0 [penwidth = 1 fontsize = 14 fontcolor = "grey28"  label="pupil"]
        
          subgraph cluster_raspi1{  
            label="Raspi 1"
            
            "raspi1" [fontname = "Courier New" shape = "Mrecord" label ="Raspi 1\n+sd card\n+psu" ];
            "displ_patient" [label="Patient Display"]
            "webcam" [label="RGB Webcam"]
            {rank=same; webcam displ_patient}
          }
          raspi1 -> displ_patient
          webcam -> raspi1
          
            //   other hardware
          "rtc" [ fontname = "Courier New" shape = "Mrecord" label ="RTC" ];
          "irlight" [label="IR Illuminator"]
          rtc -> raspi0
          rtc -> raspi1
      }
      subgraph cluster_clinician{
          label="Clinician Interface"
          
          "cpu0" [fontname = "Courier New" shape = "Mrecord" label="Clinician Computer"]
          "mouse"
          "keyboard"
          "displ_clin" [ fontname = "Courier New" shape = "Mrecord" label="Clinician Display"]
          
      }
      mouse -> cpu0
      keyboard -> cpu0
      cpu0 -> displ_clin
      
      
      subgraph cluster_other_hw{
          label="Other Hardware"
          
      }
      
      
        // inter-system connections
        cpu0 -> raspi0 [label="Control"]
        raspi0 -> raspi1 [label="Control"]
        
        raspi0 -> cpu0 [label="state"]
        raspi1 -> raspi0 [label="state"]
    }
```

# Parts List

| Name | Distributor | Number | Link | Datasheet |
| :--- | :----------- | -----: | ---- | --------- |
| Raspberry Pi 4B - 8GB | Adafruit | 1 | https://www.adafruit.com/product/4564 | |
| AAmp60 | HiFiBerry | 1 | https://www.hifiberry.com/shop/boards/hifiberry-aamp60/ | |
| DAC+ADC Pro | HiFiBerry | 1 | https://www.hifiberry.com/shop/boards/hifiberry-dac-adc-pro/ | | 
| Speakers | | 2 | | |
| RTC | | | | |
| NoIR Camera? | | | | |
| Interface/Screen? | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

