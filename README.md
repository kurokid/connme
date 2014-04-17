===============================
Connme
===============================

Client for Hostapd
A simple application to facilitate the creation of the Wireless Access Point using hostapd.


Features
--------
* Create an AP (Access Point).
* Choose one of the following encryptions: WPA, WPA2, WPA/WPA2, Open (no encryption).
* List all connected client.
* Stop internet connection for each client.

## Dependencies
* hostapd
* iw
* dnsmasq
* haveged (optional)
* python2-pyqt4

### TODO
* Limit speed for each client
* Add description and image based on client mac address
* Notification when client connect and disconnect

### LICENSE
Free software: GPL license

### Thanks To
* Oblique <https://github.com/oblique> for his "create_ap" bash script
