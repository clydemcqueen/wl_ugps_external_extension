## Testing

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
