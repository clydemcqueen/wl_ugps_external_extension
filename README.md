# WL UGPS External 

Send NMEA position information (GGA and HDT) to the [Water Linked UGPS](https://waterlinked.com/underwater-gps-g2) API.

## Typical Configuration

Add a satellite compass to the topside vessel and connect it to the ROV Ethernet network.
* It should have a static IP address on the 192.168.2.X subnet
* It should send GGA and HDT messages via UDP to BlueOS at 192.168.2.2:6200

Install this extension in [BlueOS](https://docs.bluerobotics.com/ardusub-zola/software/onboard/BlueOS-1.1/overview/):
* Select _Extensions_ in the sidebar
* Click on _WL UGPS External_
* Click _Install_

After a few moments you should see the _WL UGPS External_ entry in the sidebar.
Click on it to see a very simple UI.

## Arguments

* `UGPS_HOST` is the IP address of the WL UGPS G2 box, the default is `http://192.168.2.94`
* `SEND_RATE` is the rate to send position information to the G2 box, the default is 2Hz

## Caveats

* The G2 box still needs a GPS fix to synchronize its clock.

## Releases

### v1.0.2

* Update requirements.txt, setup.py
* No user-visible changes

### v1.0.1

* Simplified README

### v1.0.0

* Initial release

## Developer notes

See https://github.com/clydemcqueen/wl_ugps_external for testing tools.
