Installation
============

All installations follow the same pattern: use a DFU tool to flash the
dfu to the transmitter, then reboot the transmitter in USB mode and
update the file system. The transmitter may fail to boot if you try
booting deviation before updating the file system.

The :ref:`preparation` section covers things you need to do before
starting an installation. The two installation sections covers the
actual installation, depending on which tool you are using. There are
section following that include notes specific to upgrading from or to
various versions and build types.

.. _preparation:

Preparation
-----------

First download and unzip the deviation-devoXX-x.y.z.zip firmware from
http://deviationtx.com/downloads-new/category/1-deviation-releases
where XX is the number of your Walkera Devo™ transmitter. x.y.z
identifies the deviation version number. Normally you should use the
latest one.

DFU installation is done using a DfuSe tool. You can use the Walkera
'DfuSe USB Upgrade' tool for Windows to do this. You can also use the
'Deviation Uploader'.  The 'Deviation Uploader' runs on Macs, Linux or
other Unix system with usblib support as well as Windows.
.. if:: devo10
If your transmitter is a Devo F7 or F12E, you **must** use the Deviation
Uploader.
.. endif::

.. cssclass:: bold-italic

NOTE: Do NOT attempt to use the DfuSe tool from STMicroelectronics!

You can download the Walkera tool from:
https://drive.google.com/drive/u/0/folders/0B6SupsT8-3_BYXNQM1dOUlRYcGM

The Deviation Uploader can be downloaded from
http://deviationtx.com/downloads-new/category/161-dfu-usb-tool

If you are using Windows, you need to install the appropriate
drivers. See the section on :ref:`windows_drivers`

Unzip the tools and install them locally. It is recommended that you
test the DFU tool by first upgrading your TX to a different version of
Walkera firmware.

If you are upgrading from a previous Deviation release, it is strongly
recommended that you back-up the 'models' directory from the
transmitter as well as the 'tx.ini' and the 'hardware.ini' files to
ensure you don’t lose any model or transmitter configuration.

.. _windows_drivers:

Windows Driver Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Walkera DfuSe tool and the deviation uploader use different
drivers. Both can be installed by the Deviation USBDrv Installer,
available from
http://www.deviationtx.com/downloads-new/category/161-dfu-usb-tool

.. cssclass:: bold-italic

You will also need to install java from http://www.java.com/ if you
haven't already installed it.

Extract the Deviation USBDrv Installer, and run 'DFU USBDrv
Installer-x.y.exe'. You can then uninstall both drivers, or install
either the Deviation USB Driver for use with the Deviation
Uploader. Install the driver for the DfuSe tool you plan on using.


DFU Installation With Walkera DfuSe
-----------------------------------

Installation of Deviation with the Walkera DfuSe tool is done in
exactly the same manner as upgrading the Walkera Devention firmware.
Note that Deviation will NOT overwrite Walkera models stored on the
transmitter. While they cannot be accessed by Deviation, they will be
safely preserved should the Walkera firmware ever need to be
reinstalled

.. cssclass:: bold-italic

.. if:: devo10
NOTE: As a result of memory limitations with the Devo7e and Devo F12e
and Devo F7, firmware, the original models will be lost when switching
to Deviation.
.. endif::

.. image:: images/DFuSe_USB_Upgrade.png
   :width: 80%

Plug the transmitter into the PC via USB, and turn on the transmitter while holding ‘EXT’ to enter programming mode.
.. if:: devo8
On the Devo12, this is done by holding the trainer switch instead.
.. endif::

Several users have reported compatibility issues with Windows™ and/or USB ports when running this tool. If Dfuse do not recognition your TX, try removing all USB devices and restart your PC with only the USB connection to the TX.

If your transmitter has been connected correctly 'STM Device in DFU Mode' will be displayed under 'Available DFU Devices'. Otherwise this field will remain blank.

1) Press the '…' button and select the deviation-devoXX-vx.y.z.dfu file to install.
2) Select '**Upgrade**' to install the firmware. This will be grayed-out if your transmitter is not detected.  **Do NOT use 'Upload' as this will destroy the dfu file on your PC.**
.. if:: devo8
3) **Devo12 Only**: Select the 'Library' tab, click '…' select the devo12-lib.dfu from the zip file.  Then select '**Upgrade**' again to install the library.
.. endif::

Turn off the transmitter, and turn back on while holding 'ENT'. There should be a USB logo on the screen. If this is a first-time install of Deviation, the PC should prompt to format a drive. Format using default options.

DFU Installation with Deviation Uploader
----------------------------------------

.. cssclass:: bold-italic

The 'Deviation Uploader' is a jar file run with Deviation. You can
either pass the jar file to the Java executable on the command line,
or open the file in the GUI, using the Java application to open it.

Once the 'Deviation Uploader' is open, connect your transmitter to a
USB port, and then turn it on while holding down the 'EXT' button.
.. if:: devo8
On the Devo12, this is done by holding the trainer switch instead.
.. endif::

If everything is working properly, you shold see the 'Transmitter'
change to the type of the connected transmitter. If it changes to the
wrong transmitter type, stop now and seek help from the forums. If it
doesn't change, check the system information to see if the device is
listed at all. If it shows up as an unknown device on Windows, then
check your driver installation and try unplugging all other USB
devices.

1) Press the '…' button and select the deviation-devoXX-vx.y.z.dfu
   file to install.
2) If this is an initial install, select all the 'Replace' boxes.
.. if:: devo10
   On the Devo F7 and Devo F12E initial install, select the 'Format'
   check box.
.. endif::
.. if:: devo8
   On the Devo 12 and 12S, select the 'Library' check box. `(Is this correct?)`
.. endif::
3) Click the 'Install/Upgrade' option.

.. if:: devo10
   On the F7 and F12E, you are done.

.. cssclass:: blod-italic

   Do not enable USB mode, as the
   file system cannot be accessed from the desktop, and you need to
   use the 'File Manager' tab on the 'Deviation Uploader' to manage files.
.. endif::

Turn off the transmitter, and turn back on while holding 'ENT'. There should be a USB logo on the screen. If this is a first-time install of Deviation, the PC should prompt to format a drive. Format using default options.


Updating the file system via USB
--------------------------------

.. if:: devo10
.. cssclass:: bold-italic

   On the Devo F7 and F12E, do not enable USB mode, as the file system
   cannot be accessed from the desktop, and you need to use the 'File
   Manager' tab on the 'Deviation Uploader' to manage files. If you
   enable it, all you can do is format the drive, which will destroy
   your installation.
.. endif::

Now open the folder of the zip and copy all the files and directories
inside this folder to the root of the transmitter USB drive. For
details of the file-system please see :ref:`usb-file-system`. The
files with the extension zip, and dfu need not to be copied.

.. image:: images/|target|/ch_install/dont_copy_files.png
   :height: 6cm

If you are upgrading from an older release, don't update the 'tx.ini',
and 'hardware.ini' files or the 'models' directory. Optionally, copy
the 'models' directory to the transmitter except for the currently
configured model files. This last step will ensure that the defaults
for newly created models have the latest options set. If the 'tx.ini'
file is overwritten, the stick calibration must be repeated and any
settings reset.

Updating the file system with 'Deviation Uploader'
--------------------------------------------------
.. if:: devo10
.. cssclass:: bold-italic

The Devo F7 and F12E do not support access via USB. Do not turn it on,
as formatting the disk from your desktop will destroy your deviation
installation.

.. endif::

To be done.

Deviation 4.0.1
---------------

If you are upgrading from the Deviation 4.0.1 release and have
installed extra hardware, things have changed. Most notably, the
hardware configuration information has moved from 'tx.ini' to
'hardware.ini'. You'll need to move your changes to 'tx.ini' to
'hardware.ini'.

Also, the hardware connections have changed for some modules, allowing
better control of the module and telemetry on some of them. See the
module list at
https://bitbucket.org/PhracturedBlue/deviation/wiki/ModuleList
for current details.

Nightly Deviation Builds
------------------------

The Nightly builds are versions of Deviation with additional features
beyond the Deviation 4.0.1 release version.  The Nightly builds are
provided to allow the Deviation community to fully exercise new
features so the community can provide feedback and suggestions for
improvement.  As a user, you recognize that Deviation is a community
supported software system, and members of this community can
contribute by verifying, validating or commenting on the features that
they've used.

These builds are published when new features are added to the
Deviation core feature set, when major bugs are corrected and when new
hardware support is added.  The nightly builds are tested but not to
the rigorous extent of a full release.  Please read this post!
http://www.deviationtx.com/forum/5-news-announcements/1416-nightly-builds

The ONLINE User Manual for Deviation is regularly reviewed and updated
to include information about new common features.  Additionally, while
best efforts are made by the Deviation community to update these User
Guides, this documentation MAY NOT fully describe the features of the
nightly builds.  Any Deviation user with an update or change to the
manual can submit additions and changes via the Deviation Bug Tracker
at http://deviationtx.com/mantisbt

So should you load the Deviation 4.0.1 release or should you load a
Nightly?  Your own requirements will determine the answer to that
question.  If you use Walkera, Spectrum and Flysky models, and any
number of variations of the WLToys V2x2 quads, the Deviation 4.0.1
release will be sufficient.  If you have one of many newer small
quads, or if you want support for additional hardware beyond
additional transmitter modules, you should consider using the Nightly
build.

If you are also adding hardware modifications, such as switches or
transmitter modules, you should install the Deviation Nightly build
first and review the available features.  After Deviation is running,
install your hardware and modify any settings to support your
modifications.  This helps you determine the source of issues later
for troubleshooting.


Test Builds
-----------

Test Builds are for experienced users only.  The Deviation Test builds
are prepared by software developers to test new features or hardware
options, and require a higher level of experience.  These builds may
also require specific transmitter configuration or hardware mods.

Some test builds require that you install the latest Nightly prior to
installation.  DO NOT INSTALL A TEST BUILD until you read the thread
detailing the reason for that build and how to use it, and know why
you would want to use it.

Once you install a test build, **do** add a post to the appropriate
thread letting the developer know how things went! That's why they are
created - so developers can get feedback, even if it's only a note
that things worked fine.


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
