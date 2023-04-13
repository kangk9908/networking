# RCMP - Reliable Message-Based Protocol for File Transfer

1. This project is based on https://docs.google.com/document/d/19--3X5IwwDtJxeIE13WgtKm-gswR6fF8bejL468gIpo/edit#heading=h.r7wm0ewuayds

## To Run
- Sender.py
  - Prerequisite: Have file to send ready
  - ```python3 Sender.py -f FILENAME -v```
  - Arguments
    ```
       -p     # TCP port the server is listening on (default 12345)
       -f     # Name of FILE (REQUIRED)
       -s     # IP Address (default = 0.0.0.0)
       -v     # turn verbose output on
    ```
    
- Receiver.py
  - ```python3 Receiver.py -f OUTPUT_FILENAME -v```
  - Arguments
    ```
      -n      # name to be prepended in messages (default: machine name)
      -s      # server hostname or IP address (default 127.0.0.1)
      -p      # TCP port the server is listening on (default 12345)
      -f      # NAME OF FILE
      -v      # turn verbose output on
    ```
- Check if file transfer was successsful
  ```
  md5sum SENT_FILENAME
  md5sum RECEIVED_FILENAME
  ```
