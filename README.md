# Honeygain-OVPN

Spawn multiple Honeygain instances all over the world from one machine!

## How?
Honeygain provides an image that can be used to run a client on any machine that can run Docker.
Releasing their client as a docker image has an interesting side effect: it allows you to run multiple instances
of the client, all with independent networking capabilities.

What this project does is simple: it allows you to build a docker image that wraps around Honeygain's official image,
installs and runs an OpenVPN client inside the container, and then runs the Honeygain client. This will make your
container appear to Honeygain as if it's in a different country, using a different IP, while it's actually still running
on your machine. All that without routing your main PC's internet through the tunnel, or affecting other client instances.

## The caveats

There are some conditions that you will have to meet in order to use this project effectively.

First, [according to their own blog post](https://honeygain.zendesk.com/hc/en-us/articles/360011078760-Error-Unusable-network),
you are not able to connect using IP ranges that are flaged as **Data Center (DCH)** or **Reserved (RSV)**. Unfortunately,
this is the case for most major VPN providers and VPS hosting services. To check if this affects you, try visiting https://www.ipinfodb.com/
and look at the "Usage Type" field.
<br>
Different VPN locations can have different IP types, so make sure to test all of them. You're usually better off installing your
own VPN server on a remote device, or using a VPN provided by your institution as these are less likely to be flagged.

Second, Honeygain's "2 devices per IP" rule still applies, so make sure that your containers actually get assigned different IPs by
checking the logs (the external IP is logged on every start).
Again, institution VPNs are kind of perfect for this, as some of them actually assign you a dedicated IP from one of their pools!
This essentially means that you can connect to the same location multiple times and get a new IP every time.

## Okay, understood. Now how do I use this?

First, you should obtain OpenVPN configs for the different locations that you want to connect to.

< more explanation here >

Second, you're gonna have to build the image:
```shell
docker build . -t honeygain-ovpn
```

This will pull the latest official Honeygain client from DockerHub and build the `honeygain-ovpn` image, which can be used by
all your containers.

After building the image, you are now able to create your containers.

< more info >
