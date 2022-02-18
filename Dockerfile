FROM honeygain/honeygain:latest

# Install the VPN, we need root for this
USER root
RUN apt-get update \
&& echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
&& apt-get upgrade -y -q \
&& apt-get install -y dialog apt-utils \
&& apt-get install -y -q --no-install-recommends \
openvpn procps curl

# Aetup our entrypoint script
COPY entry.sh /app
RUN chmod +x entry.sh
WORKDIR /app

ENTRYPOINT ["./entry.sh"]
