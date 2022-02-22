types
=======================

Representations of data and parameters used throughout the system.

Here are some of the basic relationships between the basic types mapped to
show how they relate in order to derive a patient's audiogram

.. graphviz::

    digraph {
      charset="utf-8";

    //   modules
      subgraph modules{
          patient [ style="filled" shape=folder]
          psychophys [ style="filled" shape=folder]
          sound [ style="filled" shape=folder]
          video [ style="filled" shape=folder]
          {rank=max; patient psychophys sound video}
      }
      //   individual types
      Patient [ style="bold" shape=box3d]
      Biography [ style="bold" shape=box3d]
      Sample [ style="bold" shape=box3d]
      Samples [ style="bold" shape=box3d]
      Threshold [ style="bold" shape=box3d]
      Audiogram [ style="bold" shape=box3d]
      Sound [ style="bold" shape=box3d]
      Pupil_Params [ style="bold" shape=box3d]
      Dilation [ style="bold" shape=box3d]
      Pupil [ style="bold" shape=box3d]


      //   group into modules
      Patient -> patient
      Biography -> patient
      Sample -> psychophys
      Samples -> psychophys
      Threshold -> psychophys
      Audiogram -> psychophys
      Sound -> sound
      Pupil_Params -> video
      Dilation -> video
      Pupil -> video

    //   add attrs
      name -> Biography
      dob -> Biography
      freq_thresh [label="frequency"]
      freq_sound [label="frequency"]
      freq_thresh -> Threshold
      threshold -> Threshold
      confidence -> Threshold
      freq_sound -> Sound
      amplitude -> Sound
      duration -> Sound
      pupil_thresh [label="threshold"]
      max_diam_thresh [label="max_diameter"]
      pupil_thresh -> Pupil_Params
      max_diam_thresh -> Pupil_Params
      diameters -> Dilation
      max_diam_dil [label="max_diameter"]
      max_diam_dil -> Dilation
      response -> Pupil


    //   connect types
      Biography -> Patient
      Samples -> Patient
      Audiogram -> Patient
      Pupil -> Sample
      Sample -> Samples
      Sound -> Sample
      Threshold -> Audiogram
      Sound -> Pupil
      Dilation -> Pupil
      Pupil_Params -> Pupil

    }

.. todo::

    Replace this with an ``inheritance-diagram`` directive, as this is hard to keep up to date.


.. automodule:: perceptivo.types
   :members:
   :undoc-members:
   :show-inheritance:


.. toctree::

   gui
   networking
   patient
   psychophys
   pupil
   sound
   units
   video