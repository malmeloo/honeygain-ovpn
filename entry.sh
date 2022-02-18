#!/bin/bash

_term() {
	echo "Shutting down..."
	echo
	echo "Killing honeygain"
	pkill honeygain
	echo "Killing openvpn"
	pkill openvpn
	exit 0
}
trap _term SIGTERM

echo "-- Starting OpenVPN"
exec 3< <(openvpn --config  /config.ovpn)
sed '/Initialization Sequence Completed$/q' <&3 ; cat <&3 &

echo
echo "-- OpenVPN Started"
echo "-- Public IP: $(curl -s https://api.ipify.org/?format=text)"
echo
echo "/***************************\\"
echo "|    Honeygain OpenVPN      |"
echo "\\***************************/"
echo

su - appuser
./honeygain $@
