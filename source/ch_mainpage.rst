Main Page
=========

The standard main page layout is as follows:

.. image:: images/|target|/ch_mainpage/main_page.svg
   :width: 100%

**Current Model**: The name of the current model. Clicking the label will open up the Model Load page.  The model is configured from section `Model setup (Std & Adv GUI)`_.

**Battery Voltage**: Numerical representation of current transmitter battery state.

**Transmitter Power**: This indicates the currently selected transmitter power. It is configured from section `Model setup (Std & Adv GUI)`_.

**Current Time**: This indicates the current time (on Devo12 transmitters only).  The time is set from section `Transmitter config`_. 

**Model Icon**: An image representing the current model. It is configured from section `Model setup (Std & Adv GUI)`_.  Pressing the icon will take you to that page.

**Trims**: The trim display can be configured to show up to 10 different horizontal and vertical trims.

**Displays**: These items can be text-boxes containing input, channel, telemetry, or timer data; bar graphs displaying channel data; or icons / toggles displaying specific states (ex. gear, flaps,…).

**Quick Menus**: Quick menus can be reached via a long UP/DN press.  They can be defined from section 8.7 Main page config (Std & Adv GUI).

Safety System
-------------

.. macro:: floatimg images/|target|/ch_mainpage/safety.png

Deviation has a safety system to prevent starting up in a dangerous state (for instance spinning up the main rotor of a helicopter accidentally). The safety system works by verifying that specific conditions are met before starting to transmit to the model.  By default the output channel associated with the throttle stick must be minimum.  The Deviation firmware does not include a mechanism to define new safety conditions, however, they can be added by directly modifying the model.ini file.
While the safety message is displayed, the transmitter will not communicate with the model.  This message may appear either when initially turning on the transmitter, or when switching to a different model. The message will disappear automatically once all safety conditions have been met or when 'OK' is pressed.  In either case, Deviation will start communication with the model once the dialog is dismissed.
