This file is intended to help Jules (or any other AI agent) complete tasks associated with this repository.

This repository contains a BlueOS extension.
You can find documentation about BlueOS and extensions here:
* https://blueos.cloud/docs/stable/usage/overview/
* https://blueos.cloud/docs/stable/development/extensions/

The wl_ugps_external_extension provides a data bridge between the Advanced Navigation GNSS Compass
and the Water Linked Underwater GPS system. The GNSS compass is the _external_ source of GPS and heading
information, and this information overrides the _internal_ GPS and compass sensors in the UGPS G2 box.
You can find more information here:
* https://www.advancednavigation.com/inertial-navigation-systems/satellite-compass/gnss-compass/
* https://waterlinked.com/underwater-gps

There is a different BlueOS extension, maintained by the Water Linked team, that provides
a data bridge between the G2 and ArduSub. You can find that extension here:
* https://github.com/waterlinked/blueos-ugps-extension

ArduSub is the control software for the BlueROV2. You can find more information here:
* https://ardupilot.org/sub/

There are several goals for this extension:
* Listen for NMEA sentences from the GNSS Compass and send the global pose to the G2 box.
* Provide a simple UI that allows the ROV pilot to see that the system is working.
* Log the data for diagnostic purposes.

The UI is simple for a few reasons:
* It takes up very little space and consumes very little CPU.
* The pilot can quickly see that the system is working: everything is green!

The folder structure is dictated by the Dockerfile and BlueOS extension requirements:
* The app folder is copied into the docker image and will end up on the ROV.
* The app/static folder contains the UI.
* The app/static/register_service file is used by BlueOS to register the extension.
* The README.md file will be shown in the extension marketplace, so it should be kept short and only contain information relevant to the ROV pilot.
* The requirements.txt file is used to install the Python dependencies in the docker image.

This extension uses Python 3.9.

See testing and deployment information in [testing.md](testing.md).