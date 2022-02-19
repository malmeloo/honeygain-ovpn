# Honeygain-OVPN

Spawn multiple Honeygain instances all over the world from one machine!

## But why?

Honeygain pays you more if you have multiple devices on many different IPs. So I thought, why not put my VPN to good use and
deploy some clients worldwide? They still don't pay you much (~$9 per month in my case, running 8 containers and an android
phone), but everything is deployed from a google cloud instance that costs me less than $1 per month. It requires very little
maintenance other than the occasional reboot because my VPN provider disconnected one of my containers.

<details>
  <summary>Screenshots</summary>
  
  Can you see when I deployed the containers?
  ![image](https://user-images.githubusercontent.com/32306794/154802824-92c22a6d-92d5-428d-bc63-1e56e54c26cb.png)
  
  The running containers from my Google cloud instance
  ![image](https://user-images.githubusercontent.com/32306794/154803340-75887785-5c06-4e98-9f00-94a7e1d615d7.png)
  
  What the devices look like in my Honeygain dashboard
  ![image](https://user-images.githubusercontent.com/32306794/154803050-dac9bd43-f529-46cc-87af-007e7d660bff.png)

</details>


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

First, you should obtain OpenVPN configs for the different locations that you want to connect to. Most VPN providers already use OpenVPN under
the hood, but not all of them allow you to actually obtain the config. Usually, you'll end up having multiple configuration files for every location
(country) that you want to connect to.

Second, you're gonna have to build the image:
```shell
docker build . -t honeygain-ovpn
```

This will pull the latest official Honeygain client from DockerHub and build the `honeygain-ovpn` image, which can be used by
all your containers.

After building the image, you are now able to create your containers. They need quite some parameters to ensure that everything goes
smoothly, which is mostly because OpenVPN needs to be able to connect properly and modify some network settings.

| **Option**     | **Value**                                                                | **Notes**                                                                                    |
|----------------|--------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| Container Name | honeygain-\<country code>                                                | Can be anything you like, but should be recognizable.                                        |
| Volume         | /path/to/config-\<country code>.ovpn:/config.ovpn                        | You should mount your OpenVPN config as a volume under /config.ovpn                          |
| Command        | -tou-accept -email \<email> -pass \<pass> -device DOCKER_\<country code> | "-device" flag can be anything you like, but again, make it recognizable.                    |
| Privileged     | true                                                                     | Necessary for OpenVPN to work                                                                |
| Sysctls        | net.ipv6.conf.all.disable_ipv6=0                                         | IPv6 should be enabled (= set to 0), otherwise your VPN might not connect properly           |
| Capabilities   | NET_ADMIN                                                                | Necessary for OpenVPN to work                                                                |
| Restart        | unless-stopped                                                           | Does not matter much for functionality, but you likely want your containers to keep running. |

<br>

Example command:
```shell
docker run -d \
    --name "honeygain-nl" \
    -v "$(pwd)/configs/config-nl.ovpn:/config.ovpn" \
    --privileged \
    --sysctl "net.ipv6.conf.all.disable_ipv6=0" \
    --cap-add "NET_ADMIN" \
    --restart "unless-stopped" \
    honeygain-ovpn "-tou-accept -email my-email@ex.com -pass my-pass -device DOCKER_NL"
```
