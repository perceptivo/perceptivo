# Overview

# Hardware Block Diagram

```{eval-rst}
.. graphviz::
    
    digraph g {
      graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir = "LR"];
      ratio = auto;
      
      subgraph cluster_raspi0 {
          label="Raspi 0"
          "raspi0" [fontname = "Courier New" shape = "Mrecord" label ="Raspi 0" ];
          "dacadc"  [fontname = "Courier New" shape = "Mrecord"  label ="HifiBerry\n DAC+ADC Pro" ];
          "aamp60"  [fontname = "Courier New" shape = "Mrecord" label ="HiFiBerry\nAAmp60" ];
          "speaker_l"  [fontname = "Courier New" shape = "Mrecord" label ="Speaker (L)" ];
          "speaker_r"  [fontname = "Courier New" shape = "Mrecord" label ="Speaker (R)" ];
          "microphone"  [ fontname = "Courier New" shape = "Mrecord" label ="Microphone" ];
          "noir" [ fontname = "Courier New" shape = "Mrecord" label ="NoIR Camera" ];
        {rank=same; noir dacadc}
        {rank=same; aamp60 microphone}
      }
    
      "rtc" [ fontname = "Courier New" shape = "Mrecord" label ="RTC" ];
      "raspi1" [fontname = "Courier New" shape = "Mrecord" label ="Raspi 1" ];
      "state9" [ style = "filled" penwidth = 1 fillcolor = "white" fontname = "Courier New" shape = "Mrecord" label =<<table border="0" cellborder="0" cellpadding="3" bgcolor="white"><tr><td bgcolor="black" align="center" colspan="2"><font color="white">State #9</font></td></tr><tr><td align="left" port="r2">&#40;2&#41; e -&gt; r &bull;</td><td bgcolor="grey" align="right">$</td></tr></table>> ];
      raspi0 -> dacadc 
      dacadc -> raspi0
      dacadc -> aamp60
      aamp60 -> dacadc
      microphone -> dacadc
      aamp60 -> speaker_l
      aamp60 -> speaker_r [ penwidth = 1 fontsize = 14 fontcolor = "grey28" label = "'*'" ];
      noir -> raspi0
      rtc -> raspi0
      rtc -> raspi1
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

