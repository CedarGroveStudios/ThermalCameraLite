Introduction
============




.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/CedarGroveStudios/ThermalCameraLite/workflows/Build%20CI/badge.svg
    :target: https://github.com/CedarGroveStudios/ThermalCameraLite/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

A lighter version of the original PyGamer/PyBadge thermal imaging tool.

NOTE: Only the ``code.py`` file in the ``thermalcameralite_bundle`` is different than the original Thermal Camera code.

.. image:: https://github.com/CedarGroveStudios/ThermalCameraLite/blob/main/media/graphics/DSC06005a.jpg
  :width: 500
  :alt: PyGamer Thermal Camera

The Thermal Camera Lite is a portable AMG8833-based thermopile array imager device
implemented using CircuitPython on an Adafruit PyGamer or PyBadge SAMD51 handheld
gaming platform.

Features include measurement and imaging of 225 discrete temperatures within the
range of 0 to 80 degrees Celsius, adjustable color display gradient range,
image snapshot, and an automatic temperature range focus option. The
PyGamer/PyBadge platform provides the color display, control buttons, a speaker
for the audible cues (https://www.adafruit.com/product/4227), and room for a
LiPo rechargeable battery (https://www.adafruit.com/product/4237).

This implementation uses the Adafruit AMG8833 Thermal Camera FeatherWing
(https://www.adafruit.com/product/3622). The breakout board version of the
camera (https://www.adafruit.com/product/3538) could be used via the Stemma
interface in cases where the camera is mounted independently of the
PyGamer/PyBadge unit.

Refer to the Adafruit Learning Guide's assembly instructions for the hardware portion,
the *Improved AMG8833 PyGamer Thermal Camera Learning Guide*:
(https://learn.adafruit.com/improved-amg8833-pygamer-thermal-camera).

More details about the Thermal Camera can be found in the original repository: (htpps://github.com/cedargrovestudios/thermalcamera).

Project Description
===================

This lighter version of the Thermal Camera is identical to the original version except the setup, histogram, and alarm code was removed to reduce the memory footprint. The display resolution and overall performance (including image frame rate) did not change.

In addition to Adafruit libraries, the Thermal Camera Lite utilizes a number of PyGamer/PyBadge-stored files and conversion helpers in order to operate:
 -  ``thermalcameralite_code.py`` (renamed to code.py), the primary code module compatible with CircuitPython 8.0.x, stored in the root directory
 -  ``thermalcamera_config.py``, a Python-formatted list of default operating parameters, stored in the root directory
 -  ``thermalcamera_splash.bmp``, a bitmapped graphics file used for the opening splash screen, stored in the root directory
 -  ``OpenSans-9.bdf``, a sans serif font file, stored in the ``fonts`` folder
 -  ``thermalcamera_converters.py``, helpers for temperature conversion, stored in the root directory
 -  The ``iron.py`` spectrum helper, stored in the ``index_to_rgb`` folder (from CedarGroveStudios/CircuitPython_RGB_SpectrumTools and Adafruit/CircuitPython_Community_Bundle)

Dependencies
=============
This project depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

* `Adafruit PyGamer <https://www.adafruit.com/product/4242>`_

* `Adafruit PyBadge <https://www.adafruit.com/product/4200>`_


Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.
