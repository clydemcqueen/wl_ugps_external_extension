FROM python:3.9-slim-bullseye

COPY app /app
RUN python /app/setup.py install

# For web app:
EXPOSE 8080/tcp

# For NMEA messages from the GPS/compass:
EXPOSE 6200/udp

LABEL version="v1.0.3"

# Reference:
# https://docs.bluerobotics.com/ardusub-zola/software/onboard/BlueOS-1.1/development/extensions/
# https://docs.docker.com/engine/api/v1.41/#tag/Container/operation/ContainerCreate
LABEL permissions='\
{\
  "ExposedPorts": {\
    "8080/tcp": {},\
    "6200:6200/udp": {}\
  },\
  "HostConfig": {\
    "PortBindings": {\
      "6200/udp": [\
        {\
          "HostPort": "6200"\
        }\
      ],\
      "8080/tcp": [\
        {\
          "HostPort": ""\
        }\
      ]\
    }\
  },\
  "Env": [\
    "UGPS_HOST=http://192.168.2.94",\
    "SEND_RATE=2.0"\
  ]\
}'
LABEL authors='[\
    {\
        "name": "Clyde McQueen",\
        "email": "clyde@mcqueen.net"\
    }\
]'
LABEL company='{\
        "about": "",\
        "name": "Discovery Bay",\
        "email": "clyde@mcqueen.net"\
    }'
LABEL type="device-integration"
LABEL tags='[\
    "positioning",\
    "navigation",\
    "short-baseline"\
]'
LABEL readme='https://raw.githubusercontent.com/clydemcqueen/wl_ugps_external_extension/{tag}/README.md'
LABEL links='{\
    "website": "https://github.com/clydemcqueen/wl_ugps_external_extension",\
    "support": "https://github.com/clydemcqueen/wl_ugps_external_extension/issues"\
}'
LABEL requirements="core >= 1.1"

ENTRYPOINT cd /app && python main.py --ugps_host $UGPS_HOST --send_rate $SEND_RATE
