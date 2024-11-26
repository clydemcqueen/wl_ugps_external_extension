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

* Set `UGPS_HOST` to the IP address of the WL UGPS G2 box. The default is `http://192.168.2.94`.
* Set `SEND_RATE` to the rate to send position information to the G2 box. The default is 2Hz.
* Set `POLL_RATE` to the rate to poll the G2 box for acoustic and pose information. The default is 0 (no polling).
* If `LOG_NMEA` is `--log_nmea`, then NMEA messages will be logged. The default is blank (no logging). 

You can provide custom arguments in BlueOS. For example, you can enable logging using [these arguments](custom_args.json):
~~~
{
  "Env": [
    "UGPS_HOST=http://192.168.2.94",
    "SEND_RATE=2.0",
    "POLL_RATE=5.0",
    "LOG_NMEA=--log_nmea"
  ]
}
~~~

Logs can be found in BlueOS:

* Select _File Browser_ in the sidebar
* Click on _extensions_
* Click on _wl_ugps_external_

## Caveats

* The G2 box still needs a GPS fix to synchronize its clock.

## Releases

### v1.1.0-beta.1

* Optional: Log GGA, HDT and PASHR messages
* Optional: Poll the G2 box for additional information (pose, acoustic solution) and log the results

### v1.0.3

* Shorten company name
* No user-visible changes

### v1.0.2

* Update requirements.txt, setup.py
* No user-visible changes

### v1.0.1

* Simplify README

### v1.0.0

* Initial release

## Developer notes

See [wl_ugps_external](https://github.com/clydemcqueen/wl_ugps_external) for testing tools.
