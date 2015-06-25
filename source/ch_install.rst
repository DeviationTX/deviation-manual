Installation
============

New installation
----------------
Installation of Deviation is done in exactly the same manner as upgrading the Walkera Devention firmware.  Note that Deviation will NOT overwrite Walkera models stored on the transmitter. While they cannot be accessed by Deviation, they will be safely preserved should the Walkera firmware ever need to be reinstalled 

.. cssclass:: bold-italic

.. if:: devo10
NOTE: As a result of memory limitations with the Devo7e and devo 12
firmware, the original models will be lost when switching to
Deviation.
.. endif::

First download and unzip the deviation-devoXX-x.y.z.zip firmware from http://www.deviationtx.com/repository/Deviation-Releases/ where XX is the number of your Walkera Devo™ transmitter. x.y.z identifies the deviation version number. Normally you should use the latest one.

Upgrading is done using the Walkera ‘DfuSe USB Upgrade’ tool for Windows. You can download this tool directly from Walkera: 

http://www.walkera.com/en/upload/upgrade/DevoDfuSe%20V2.0.zip. 

.. cssclass:: bold-italic

NOTE: Do NOT attempt to use the DfuSe tool from STMicroelectronics!

Unzip the upgrade tool and install locally. It is recommended that you test the DFU tool by first upgrading your TX to a different version of Walkera firmware.
 
.. image:: images/DFuSe_USB_Upgrade.png
   :width: 80%

Plug the transmitter into the PC via USB, and turn on the transmitter while holding ‘EXT’ to enter programming mode.
.. if:: devo8
On the Devo12, this is done by holding the trainer switch instead.
.. endif::

Several users have reported compatibility issues with Windows™ and/or USB ports when running this tool. If Dfuse do not recognition your TX, try removing all USB devices and restart your PC with only the USB connection to the TX. 

If your transmitter has been connected correctly 'STM Device in DFU Mode' will be displayed under 'Available DFU Devices'. Otherwise this field will remain blank.

1) Press the '...' button and select the deviation-devoXX-vx.y.z.dfu file to install.
2) Select '**Upgrade**' to install the firmware. This will be grayed-out if your transmitter is not detected.  **Do NOT use ‘Upload’ as this will destroy the dfu file on your PC.**
.. if:: devo8
3) **Devo12 Only**: Select the 'Library' tab, click '…' select the devo12-lib.dfu from the zip file.  Then select '**Upgrade**' again to install the library. 
.. endif::

Turn off the transmitter, and turn back on while holding ‘ENT’. There should be a USB logo on the screen. If this is a first-time install of Deviation, the PC should prompt to format a drive. Format using default options.


Open the folder of the zip and copy all the files and directories inside this folder to the root of the transmitter USB drive. For details of the file-system please see :ref:`usb-file-system`. The files with the extension zip, and dfu need not to be copied.

.. image:: images/|target|/ch_install/dont_copy_files.png
   :height: 6cm

Upgrade notes
-------------
If you are upgrading from a previous Deviation release, it is strongly recommended that you back-up the ‘models’ directory from the transmitter as well as the tx.ini file to ensure you don’t lose any model or transmitter configuration. Copy all directories except for the ‘models’ directory and the tx.ini file to the transmitter. Optionally, copy the ‘models’ directory to the transmitter except for the currently configured model files. This last step will ensure that the defaults for newly created models have the latest options set. If the tx.ini file is overwritten, the stick calibration must be repeated and any settings reset.

.. macro:: pdf_page_break

.. _usb-file-system:

USB & File-system
-----------------
Deviation stores all configuration, bitmaps, and models as regular files on the USB file-system. USB can be most easily enabled by holding down the ‘ENT’ button while powering up the transmitter. Files can then be easily copied to or from the transmitter.

The directory structure is as follows:

=========================  ==================================================
\\tx.ini                   Transmitter configuration. Includes trim settings, calibration data, and the last-used model
                           number
\\hardware.ini             Transmitter hardware setup, describing supported hardware modifications.
                           number
\\errors.txt               If the firmware crashes or reboots, debug information will be stored in this file
\\datalog.bin              File for telemetry data
\\media\\config.ini        The color scheme and fonts for the transmitter
\\media\\sound.ini         Contains notes to play for various alarms
\\media\\*.bmp             Images used for the current transmitter theme
\\media\\*.fon             Font files
\\models\\default.ini      The default model, loaded whenever a model is cleared
\\models\\model*.ini       Configuration files for each model. Due to a limitation in the firmware, deviation cannot
                           create new files. It is therefore necessary to have a modelxx.ini for each model regardless
                           of whether it is currently in use.
\\modelico\\*.bmp          All available model icons (96x96 pixels is recommended but not required). Model icons must
                           be saved as 16-bit BMP files in either RGB565 (non-transparent) or ARGB1555 (transparent)
                           format.
\\templates\\*.ini         Configuration files used when loading predefined templates.  These are nearly identical to
                           the model configuration files, however they do not necessarily define all parameters
\\language\\lang*.*        Language translation files.  These are UTF-8 text files containing the English string and
                           the respective translated string.
=========================  ==================================================

.. cssclass:: bold-italic

Note: Deviation only supports 8.3 style file names.  That means file names should be no larger than 'xxxxxxxx.yyy'**
