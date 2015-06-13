..

.. |mod-install-link| replace:: https://bitbucket.org/PhracturedBlue/deviation/wiki/ModuleInstallation
.. |a7105-note| replace:: **NOTE:  This protocol requires the addition of an ‘A7105’ hardware module to function.  See the following document for more information**:
.. |cc2500-note| replace:: **NOTE:  This protocol requires the addition of an ‘CC2500’ hardware module to function.  See the following document for more information**:
.. |nrf24l01-note| replace:: **NOTE:  This protocol requires the addition of an ‘NRF24L01’ hardware module to function.  See the following document for more information**:
.. |nrf24l01p-note| replace:: **NOTE:  This protocol requires the addition of an ‘NRF24L01+’ hardware module to function.  Note the "plus" version of the nRF device is required to support the 250kbits/s data rate.  See the following document for more information**:

Protocols
=========
Some protocols have additional customization or limits.  Each of the protocols is described below.  If an ‘*’ is shown before the protocol name, it means this protocol is not currently supported by the transmitter.  This generally means that the necessary hardware module is not installed or has not been configured properly.  More information can be found in the Module installation guide:

|mod-install-link|

Protocol: DEVO
--------------
The DEVO protocol is used to maintain compatibility with the Walkera DEVO receivers/models.  This protocol supports up to 12 channels.  The DEVO protocol supports both auto-binding and manual-binding.  If Fixed ID is set to ‘None’ the transmitter will attempt to auto-bind with the receiver every time it is powered on.  If a value is set for Fixed ID, the receiver must be bound manually one-time using the ‘Bind’ button, after which it should stay bound.  Note that the Fixed ID is only part of the binding procedure.  Two transmitters with the Same ID cannot control the same model.

.. macro:: floatimg images/devo8/ch_protocols/devo.png

The DEVO protocol also supports enabling/disabling the telemetry capability.  This option is accessed by pressing the Protocol spin-box when DEVO is shown.

The following fields are available in Devo Telemetry.  Note that not all models/receivers report all fields, and that some fields require extra modules to enable.

.. macro:: floatimg images/devo8/ch_protocols/devo_telem.png

.. container::

   * **Temp1/2/3/4**: Temperature readings.  These can be battery, motor, or ambient values
   * **Volt1/2/3**: Voltage readings for receiver battery, and external batteries
   * **RPM1/2**: Motor/Engine RPM values
   * **GPS Data**: Current position, speed and altitude from GPS module

Protocol: WK2801
----------------
The WK2801 protocol is used to control older Walkera models.  The previous Walkera models were segmented into 3 similar but not identical protocols: WK2801, WK2601, WK2401.  This roughly corresponds to the number of channels supported, but many of the newer 6-channel receivers actually support the WK2801 protocol.  It is recommended to try the WK2801 protocol 1st when working with older Walkera models before attempting the WK2601 or WK2401 mode, as the WK2801 is a superior protocol.  The WK2801 protocol supports up to 8 channels, and both auto-binding and manual-binding.  If Fixed ID is set to ‘None’ the transmitter will attempt to auto-bind with the receiver every time it is powered on.  If a value is set for Fixed ID, the receiver must be bound manually one-time using the ‘Bind’ button, after which it should stay bound.

Protocol: WK2601
----------------
The WK2601 protocol is used to control older Walkera models.  The previous Walkera models were segmented into 3 similar but not identical protocols: WK2801, WK2601, WK2401.  This roughly corresponds to the number of channels supported, but many of the newer 6-channel receivers actually support the WK2801 protocol.  It is recommended to try the WK2801 protocol 1st when working with older Walkera models before attempting the WK2601 or WK2401 mode, as the WK2801 is a superior protocol.  The WK2601 protocol supports up to 7 channels, and only supports auto-binding.  The fixed ID can be used, but does not prevent auto-binding during power-on.

.. macro:: floatimg images/devo8/ch_protocols/wk2601.png

The WK2601 protocol also supports additional options.  These are accessed by pressing the Protocol spin-box when Wk2601 is shown:

**Chan mode**: Sets how channels are processed:

* **5+1**: AIL, ELE, THR, RUD,  GYRO (ch 7) are proportional.  Gear (ch 5) is binary.  Ch 6 is disabled
* **Heli**: AIL, ELE, THR, RUD, GYRO are proportional.  Gear (ch 5) is binary. COL (ch 6) is linked to Thr.  If Ch6 >= 0, the receiver will apply a 3D curve to the Thr.  If Ch6 < 0, the receiver will apply normal curves to the Thr.  The value of Ch6 defines the ratio of COL to THR.
* **6+1**: AIL, ELE, THR, RUD,  COL (ch 6), GYRO (ch 7) are proportional.  Gear (ch 5) is binary.  This mode is highly experimental.
* **COL Inv**: Invert COL servo
* **COL Limit**: Set maximum range of COL servo

Protocol: WK2401
----------------
The WK2401 protocol is used to control older Walkera models.  The previous Walkera models were segmented into 3 similar but not identical protocols: WK2801, WK2601, WK2401.  This roughly corresponds to the number of channels supported, but many of the newer 6-channel receivers actually support the WK2801 protocol.  It is recommended to try the WK2801 protocol 1st when working with older Walkera models before attempting the WK2601 or WK2401 mode, as the WK2801 is a superior protocol.  The WK2401 protocol supports up to 4 channels, and only supports auto-binding.  The fixed ID can be used, but does not prevent auto-binding during power-on.

Protocol: DSM2
--------------
The DSM2 protocol is used to control many Spektrum™ and JR™, as well as other models using this protocol.  While the DSM2 protocol can support up to 14 channels, Deviation is currently limited to a maximum of 12.  Note that many receivers with less than 8 channels require the Transmitter to send 7 or less channels.  Make sure the # of channels is set appropriately for the receiver.  DSM2 does not support auto-binding.  If Fixed ID is set to None, a transmitter-specific ID is used instead.  It is necessary to manually bind each model before the first use.

.. macro:: floatimg images/devo8/ch_protocols/dsm2.png

The DSM2 protocol also supports enabling/disabling the telemetry capability.  This option is accessed by pressing the Protocol spin-box when DSM2 is shown.

.. macro:: floatimg images/devo8/ch_protocols/dsm_telem.png

.. container::

   The following fields are available in DSM2 Telemetry.  Note that a dedicated telemetry module and additional sensors are needed to capture this data

   * **FadesA/B/L/R**: The number of times each antenna has received a weak signal.  Ideally these numbers should all be similar, indicating even reception to each antenna
   * **Loss**: The number of times complete signal loss (dropped frame) occurred
   * **Holds**: The number of times the receiver entered fail-safe mode due to loss of signal
   * **Volt1/2**: Battery voltage for receiver and an external source
   * **RPM**: Engine/Motor speed
   * **Temp**: Temperature from external temperature sensor
   * **GPS Data**: Current position, speed and altitude from GPS module

Protocol: DSMX
--------------
The DSMX protocol is used to control many Spektrum™ and JR™, as well as other models using this protocol.  While the DSMX protocol can support up to 14 channels, Deviation is currently limited to a maximum of 12.  Note that many receivers with less than 8 channels require the Transmitter to send 7 or less channels.  Make sure the # of channels is set appropriately for the receiver.  DSMX does not support auto-binding.  If Fixed ID is set to None, a transmitter-specific ID is used instead.  It is necessary to manually bind each model before the first use.

Note that unlike Spektrum™ or JR™ transmitters, Deviation will not automatically select between DSM2 and DSMX.  The user must select which protocol to use.

.. macro:: floatimg images/devo8/ch_protocols/dsmx.png

The DSMX protocol also supports enabling/disabling the telemetry capability.  This option is accessed by pressing the Protocol spin-box when DSMX is shown.

The list of DSMX telemetry fields is identical to those in the DSM2 Protocol, and are documented in section 9.5 Protocol: DSM2.

Protocol: J6Pro
---------------
The J6Pro protocol is used to support Nine Eagles™ models.  Only models compatible with the J6Pro transmitter can be used.  Many older 4-channel Nine Eagles models used a different protocol that is unsupported.  The J6Pro protocol supports up to 12 channels, although only models with 6 channels have been tested.  J6Pro does not support auto-binding.  If Fixed ID is set to None, a transmitter-specific ID is used instead.  It is necessary to manually bind each model before the first use.

Protocol: \*Flysky
------------------
The Flysky protocol is used to control Turnigy/Flysky receivers as well as a few other models using the same protocol (WL V911, Xieda 9958, etc).  |a7105-note|

|mod-install-link|

The Flysky protocol supports up to 8 channels, and both auto-binding and manual-binding.  If Fixed ID is set to ‘None’ the transmitter will attempt to auto-bind with the receiver every time it is powered on.  If a value is set for Fixed ID, the receiver must be bound manually one-time using the ‘Bind’ button, after which it should stay bound.

The Flysky protocol also supports additional options.  These are accessed by pressing the Protocol spin-box when Flysky is shown:

**WLToys V9x9**: Enables enhanced protocol configuration for use with WLToys V959, v969, etc models:

* Lights are controlled by Channel 5
* Video is controlled by Channel 6
* Camera is controlled by Channel 7

Note that if these channels are assigned to a switch, turning the switch on toggles the state, and turning the switch off has no effect.  Thus to turn the lights on, flip the switch assigned to Channel 5 from off to on.  Flipping the switch back to off has no effect.  Flipping the switch back on now turns the lights back off.

Protocol: \*Hubsan4
-------------------
The Hubsan4 protocol supports the Hubsan-X4 quadracopter.  No other models have been tested with this protocol.  |a7105-note|

|mod-install-link|

.. macro:: floatimg images/devo8/ch_protocols/hubsan.png

The Hubsan4 protocol supports up to 7 channels, and only supports auto-binding.  The fixed ID can be used, but does not prevent auto-binding during power-on.  The 1 st 4 channels represent Aileron, Elevator, Throttle, and Rudder.  Additional channels control the quadracopter special functions: 

* Channel 5 controls the LEDs
* Channel 6 enables ‘flip’ mode
* Channel 7 Turns video on/off

Options configurable on the Hubsan page:

* **vTX MHz**: Defines the frequency used by the Hubsan H107C video transmitter (Requires a 5.8GHz receiver capable of receiving and displaying video).
* **Telemetry**: Enable receiving of model battery voltage.

Protocol: \*Skyartec
--------------------
The Skyartec protocol is used to control Skyartec™ receivers and models. |cc2500-note|

|mod-install-link|
 
The Skyartec protocol supports up to 7 channels, does not support auto-binding.  If Fixed ID is set to None, a transmitter-specific ID is used instead.  It is necessary to manually bind each model before the first use.

Protocol: \*Frsky1
------------------
The Frsky1 protocol is used to control older (non-telemetry) Frsky™ receivers using the one-way protocol. |cc2500-note|

|mod-install-link|

The Frsky1way protocol supports 4 channels, does not support auto-binding.  If Fixed ID is set to None, a transmitter-specific ID is used instead.  It is necessary to manually bind each model before the first use.

Protocol: \*Frsky2
------------------
The Frsky2 protocol is used to control newer (telemetry enabled) Frsky™ receivers using the two-way protocol. |cc2500-note|

|mod-install-link|

The Frsky2way protocol supports up to 8 channels, does not support auto-binding.  If Fixed ID is set to None, a transmitter-specific ID is used instead.  It is necessary to manually bind each model before the first use.

The Frsky2way protocol also supports enabling/disabling the telemetry capability.  This option is accessed by pressing the Protocol spin-box when Frsky2way is shown.

Protocol: \*V202
----------------
The V202 protocol supports the WLToys V202 quadracopter. |nrf24l01-note|

|mod-install-link|

The V202 protocol supports up to 8 channels.  The 1 st 4 channels represent Aileron, Elevator, Throttle, and Rudder.  Additional channels control the quadracopter special functions: 

* Channel 5 controls the blink speed
* Channel 6 enables ‘flip’ mode
* Channel 7 Enables the camera
* Channel 8 Turns video on/off

Protocol: \*SLT
---------------
The SLT protocol is used to control TacticSLT/Anylink receivers. |nrf24l01-note|

|mod-install-link|

Protocol: \*HiSky
-----------------
The HiSky protocol is used to control HiSky brand models along with the WLToys v922 v955 models. |nrf24l01-note|

|mod-install-link|

Protocol: \*YD717
-----------------
The YD717 protocol supports the YD717 and Skybotz UFO Mini quadcopters, plus several models from Sky Walker, XinXun, Ni Hui"), and Syma through protocol options. See the Supported Modules spreadsheet for a complete list. |nrf24l01-note|

|mod-install-link|

The YD717 protocol supports 9 channels and only supports auto-binding. The protocol stays in bind mode until successful. 

The first four channels represent Aileron, Elevator, Throttle, and Rudder. 

The fifth channel enables the auto-flip function when greater than zero. Additionally to enable auto-flips left and right the aileron channel scale must be 87 or greater. Likewise for the elevator channel and front/back flips. When auto-flip is enabled, moving the cyclic all the way in any direction initiates a flip in that direction. The YD717 requires at least four seconds between each auto-flip.

The sixth channel turns on lights when greater than zero.

The seventh channel takes a picture on transition from negative to positive.

The eighth channel starts/stops video recording on each positive transition.

The ninth channel is assigned to last feature flag available in the protocol.  This may control headless mode on models that have the feature.

Protocol: \*SymaX
-----------------
This protocol is used on Syma models: X5C-1, X11, X11C, X12, new X4, and new X6.  A variant supporting the original X5C and the X2 is included as a protocol option.  (The Syma X3, old X4, and old X6 are supported with the SymaX4 option in the YD717 protocol. ) See the Supported Modules spreadsheet for a complete list. |nrf24l01p-note|

|mod-install-link|

The SymaX protocol supports 7 channels and only supports auto-binding.

The first four channels represent Aileron, Elevator, Throttle, and Rudder. 

The fifth channel is unused.

The sixth channel enables the auto-flip function when greater than zero. 

The seventh channel takes a picture when the channel moves from negative to positive.

The eighth channel starts/stops video recording on each positive transition.

Protocol: PPM
-------------
The PPM protocol is used to output PPM on the trainer port.  It will disable all radio transmission.  PPM is useful for connecting to simulators, or other radio-modules that plug into the trainer port.  The Fixed ID has no effect, and there is no binding associated with this protocol.

.. macro:: floatimg images/devo8/ch_protocols/ppm.png

.. container::

   Options configurable on the PPM page:


   * **Center PW**: Defines the time (in µsec) of the pulse that the transmitter transmits to represent to represent centered servo position.  If this number doesn’t match the master transmitter, the servos will not be centered.

   * **Delta PW**: Defines the width of the pulse (measured from center) sent by the transmitter to define max servo throw.  If this value is incorrect, the servos will not achieve full range (or will travel too much)

   * **Notch PW**: Defines the delay between the channels.

   * **Frame Size**: Defines the total time for all channels to be transferred. 

Deviation does not auto-detect when a trainer cord is plugged into the transmitter.  To use Deviation with a simulator (such as Phoenix), create a new model, name it appropriately, and select PPM as the protocol.  Use the Re-Init button or power-cycle to enable PPM.

Protocol: USBHID
----------------
The USBHID protocol will convert he transmitter into a USB joystick.  Connecting the transmitter to a PC via the USB cable will enable the transmitter to be detected as a joystick by the computer. This may be used to enable the transmitter to control any simulators that support joystick input. Some initial calibration may be necessary and is accomplished via the control panel applet of your operating system.

