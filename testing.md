# Testing

## Python version

Uses Python 3.9.

## Manual testing

### polling_thread and data_logger

This will poll the Water Linked demo server and log data to /tmp/wl_ugps_test/...
~~~
python3 app/polling_thread.py
~~~

### listen_thread and data_logger

Start the NMEA emulator in terminal 1:
~~~
python3 nmea_emulator.py
~~~

This will listen for messages on localhost and log them to /tmp/wl_ugps_test/...
~~~
python3 app/listen_thread.py
~~~

### send_thread

This will send data to the Water Linked demo server. There is no output.
~~~
python3 app/send_thread.py
~~~

## Docker testing (local)

Build and run the docker image locally:
~~~
docker build . -t YOURDOCKERHUB/wl_ugps_external_extension:local
docker run --rm -it \
  -p 8080:8080 \
  -p 6200:6200/udp \
  -e UGPS_HOST=https://demo.waterlinked.com \
  -e SEND_RATE=2.0 \
  -e POLL_RATE=2.0 \
  -e LOG_NMEA="--log_nmea" \
  --name wl_ugps_test \
  YOURDOCKERHUB/wl_ugps_external_extension:local
~~~

Run the emulator in terminal 2:
~~~
python3 nmea_emulator.py --port 6200
~~~

## Testing the extension on a Pi running BlueOS + SITL:

Step 1: set up buildx (one time):
~~~
docker buildx create --name multiarch --driver docker-container --use
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
~~~

Step 2: log into dockerhub (one time):
~~~
docker login
~~~

Step 3: Build and upload:
~~~
docker buildx build --platform linux/amd64,linux/arm/v7 . -t YOURDOCKERHUB/wl_ugps_external_extension:latest --output type=registry
~~~

Step 4: Install on BlueOS
* Extension identifier: YOURDOCKERHUB.wl_ugps_external_extension
* Extension name: wl_ugps_external_extension
* Docker image: YOURDOCKERHUB/wl_ugps_external_extension
* Docker tag: latest
* Permissions:
~~~
{
  "ExposedPorts": {
    "8080/tcp": {},
    "6200:6200/udp": {}
  },
  "HostConfig": {
    "Binds": [
      "/usr/blueos/extensions/wl_ugps_external:/data:rw"
    ],
    "PortBindings": {
      "6200/udp": [
        {
          "HostPort": "6200"
        }
      ],
      "8080/tcp": [
        {
          "HostPort": ""
        }
      ]
    }
  },
  "Env": [
    "UGPS_HOST=https://demo.waterlinked.com",
    "SEND_RATE=2.0",
    "POLL_RATE=2.0",
    "LOG_NMEA=--log_nmea"
  ]
}
~~~

Run the emulator:
~~~
python3 nmea_emulator.py --ip 192.168.2.2 --port 6200
~~~
