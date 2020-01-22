# xHID
## Status of project
Goal: I needed quick implementation of "synergy" client  protocol implementation that allows me control of Sway on Wayland.

I currently don't have any intention to extend the project scope as I hope symless will soon release version of client that will support wayland. Or maybe barrier (https://github.com/debauchee/barrier) will be faster?

If you feel you need something extra feel free to fork or update the code and post pull request :)

## Test setup, features and limitations
Currently this works as client for synergy server.
Test setup:
* Linux (arch), sway (1:1.2-5), wayland (1.17.0-1)
* Synergy PRO (1.11.0-rc2-9fecf0bc) as SERVER on Windows 10
* Python 3.8.1 on linux client

Features:
* Keyboard and mouse sharing seems to be working properly
* "Modular" design
* Attached example configuration file  it initialize modules needed to connect to synergy server and create 2 virtual devices (mouse and keyboard)

Limitations:
* I'm not full-time developer, so there might be bugs in code!
* Clipboard sharing is not implemented
* User running xhid might need some extra privileges (at least write access to /dev/uinput to be able to create virtual input device)
## Usage
* `./xhid.py -c ./sym-km.conf`
## Dependencies
* python-i3ipc (2.1.1-2)
* python-libevdev (0.8-2)

