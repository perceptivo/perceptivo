# Overview

## Hardware Block Diagram

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
              "headphones" [fontname = "Courier New" shape = "Mrecord" label="Headphones"];
              "rca" [fontname = "Courier New" shape = "Mrecord" label="RCA - 3.5mm"];
              "noir" [ fontname = "Courier New" shape = "Mrecord" label ="NoIR Camera" ];
              "psu" [ fontname = "Courier New" shape = "Mrecord" label="18V 2.6A PSU"]
            {rank=same; noir dacadc}
            {rank=same; aamp60 microphone}
            {rank=same; speaker_l speaker_r psu}
          }
          dacadc -> raspi0 [label="microphone input"]
          dacadc -> raspi0 [label="power"]
          raspi0 -> dacadc [label="sound output"];
          dacadc -> aamp60 [label="line-level sound"];
          dacadc -> rca [label="line-level sound"];
          rca -> headphones [label="line-level sound"]
          aamp60 -> dacadc [label="power"];
          microphone -> dacadc [label="line-level sound"];
          aamp60 -> speaker_l [label="amplified sound"];
          aamp60 -> speaker_r [label="amplified sound"];
          psu -> aamp60 [label="power"]
          noir -> raspi0 [penwidth = 1 fontsize = 14 fontcolor = "grey28"  label="pupil"]
        
          subgraph cluster_raspi1{  
            label="Raspi 1"
            
            "raspi1" [fontname = "Courier New" shape = "Mrecord" label ="Raspi 1\n+sd card\n+psu" ];
            "displ_patient" [label="Patient Display"];
            "webcam" [label="RGB Webcam"]
            {rank=same; webcam displ_patient}
          }
          raspi1 -> displ_patient
          webcam -> raspi1
          
            //   other hardware
          "rtc" [ fontname = "Courier New" shape = "Mrecord" label ="RTC" ];
          "irlight" [fontname = "Courier New" shape = "Mrecord" label="IR Illuminator"]
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

## Parts List

### Clinician Interface

| Name | Distributor | Number | Link | Datasheet |
| :--- | :----------- | -----: | ---- | --------- |
| Raspberry Pi 400 | Adafruit | 1 | [🛒](https://www.adafruit.com/product/4796) | {download}`📁 </datasheets/pi400-product-brief.pdf>` |
| Touchscreen | | 1 | | |
| Mouse | Newegg | 1 |  [🛒](https://www.newegg.com/logitech-910-001822-m510/p/N82E16826104382) | |

### Raspis

| Name | Distributor | Number | Link | Datasheet |
| :--- | :----------- | -----: | ---- | --------- |
| Raspberry Pi 4B - 8GB | Adafruit | 2 | [🛒](https://www.adafruit.com/product/4564) | {download}`📁 - brief </datasheets/raspi4-product-brief.pdf>`<br>{download}`📁 - mechanical </datasheets/raspi4-mechanical.pdf>`<br>{download}`📁 - circuits</datasheets/raspi4-circuit-schematic.pdf>`<br>{download}`📁 - bcm2711 </datasheets/bcm2711.pdf>` |
| USB-C 5.1V 3A PSU | Adafruit | 2 | [🛒](https://www.adafruit.com/product/4298) | |
| 18V 2.6A PSU | Digikey | 1 | [🛒](https://www.digikey.com/en/products/detail/inventus-power/IPD5018-760/6230191) | |
| Samsung 64GB Pro Endurance microSD | Newegg | 2 | [🛒](https://www.newegg.com/samsung-64gb-microsdxc/p/20-147-696) | |
| Enclosures? | | 2 | | |
| RTC? | | 1 | | |

### Audio

| Name | Distributor | Number | Link | Datasheet |
| :--- | :----------- | -----: | ---- | --------- |
| AAmp60 | HiFiBerry | 1 | [🛒](https://www.hifiberry.com/shop/boards/hifiberry-aamp60/) | [🔗](https://www.hifiberry.com/docs/data-sheets/datasheet-aamp60/) |
| DAC+ADC Pro | HiFiBerry | 1 | [🛒](https://www.hifiberry.com/shop/boards/hifiberry-dac-adc-pro/) | [🔗](https://www.hifiberry.com/docs/data-sheets/datasheet-dac-adc-pro/) | 
| Tang Band W3-1878 | Parts Express | 2 | [🛒](https://www.parts-express.com/Tang-Band-W3-1878-3-Full-Range-Driver-264-902) | [🔗](http://www.loudspeakerdatabase.com/TangBand/W3-1878) |
| Condenser Microphone | | 1 | [🛒]() | [🔗]() |
| Phantom Power Supply | | 1 | [🛒]() | [🔗]() |
| Sennheiser HDA 300 | | 1 | [🛒](https://www.bhphotovideo.com/c/product/1023207-REG/sennheiser_hda300_hda_300_audiometers_headphones.html) |  {download}`📁</datasheets/HDA300.pdf>` |
| RCA -> 3.5mm Adapter | | 1 | [🛒]() | [🔗]() |
| | | | | |

### Video

| Name | Distributor | Number | Link | Datasheet |
| :--- | :----------- | -----: | ---- | --------- |
| NoIR Camera | Adafruit | 1 |  [🛒](https://www.adafruit.com/product/3100?src=raspberrypi) | [🔗]() |
| Raspberry Pi Camera V2 | Adafruit | 1 | [🛒](https://www.adafruit.com/product/3099?src=raspberrypi) | [🔗]() |
| Touchscreen | | | [🛒]() | [🔗]() |
| Light source? | | | [🛒]() | [🔗]() |

### Etc

| Name | Distributor | Number | Link | Datasheet |
| :--- | :----------- | -----: | ---- | --------- |
| Netgear 5-Port Switch (GS105NA) | Newegg | 1 | [🛒](https://www.newegg.com/netgear-gs105-v5-5-x-rj45/p/N82E16833122128) | [🔗]() |
| Ethernet Cables (10ft) | Newegg | 3 | [🛒](https://www.newegg.com/p/N82E16812119169) | [🔗]() |
| Perixx Periboard-706plus with trackball | Newegg | 1 | [🛒](https://www.newegg.com/perixx-10532-usb-rf-wireless/p/0GA-0038-00012?quicklink=true) | [🔗]() |
| Speaker Wire | | | | |
