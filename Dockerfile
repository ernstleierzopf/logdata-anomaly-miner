# logdata-anomaly-miner Dockerfile
#
# Use build-script to create docker:
#    scripts/build_docker.sh
#
# Build manually:
#    docker build -t aecid/logdata-anomaly-miner:latest -t aecid/logdata-anomaly-miner:$(grep '__version__ =' source/root/usr/lib/logdata-anomaly-miner/metadata.py | awk -F '"' '{print $2}') .
#
# See: https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Deployment-with-Docker
#

# Pull base image.
FROM debian:bookworm
ARG UNAME=aminer
ARG UID=1000
ARG GID=1000

# allow the system to use two package managers (apt and pip), as we do it intentionally (needed since Debain Bookworm - see PEP 668
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Set local timezone
ENV TZ=Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

LABEL maintainer="wolfgang.hotwagner@ait.ac.at"

# Install necessary debian packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get update && apt-get install -y \
    supervisor \
    python3 \
    python3-pip \
    libacl1-dev \
    sudo \
    rsyslog

# Docs
RUN apt-get update && apt-get install -y \
    python3-sphinx \
    python3-sphinx-rtd-theme \
    python3-recommonmark \
    make

ADD . /home/aminer/logdata-anomaly-miner
RUN cd /home/aminer/logdata-anomaly-miner && scripts/aminer_install.sh

# For Docs
ADD docs /docs
ADD README.md /docs
ADD SECURITY.md /docs
ADD LICENSE /docs/LICENSE.md


# Copy logdata-anomaly-miner-sources
ADD source/root/usr/lib/logdata-anomaly-miner /usr/lib/logdata-anomaly-miner

# copy these files instead as symlinks would need absolute paths.
ADD source/root/etc/aminer/conf-available/ait-lds/* /etc/aminer/conf-enabled/
ADD source/root/etc/aminer/conf-available/ait-lds2/* /etc/aminer/conf-enabled/
ADD source/root/etc/aminer/conf-available/generic/* /etc/aminer/conf-enabled/
ADD source/root/etc/aminer/conf-available/ait-lds /etc/aminer/conf-available/ait-lds
ADD source/root/etc/aminer/conf-available/ait-lds2 /etc/aminer/conf-available/ait-lds2
ADD source/root/etc/aminer/conf-available/generic /etc/aminer/conf-available/generic

# Entrypoint-wrapper
ADD scripts/aminerwrapper.sh /aminerwrapper.sh

# Prepare the system and link all python-modules
RUN chmod 0755 /usr/lib/logdata-anomaly-miner/aminerremotecontrol.py \
	&& chmod 0755 /etc/aminer \
	&& mkdir -p /var/lib/aminer/logs \
    && chown $UID.$GID -R /var/lib/aminer \
    && chown $UID.$GID -R /docs \
    && chmod 0755 /aminerwrapper.sh

RUN PACK=$(find /usr/lib/python3/dist-packages -name posix1e.cpython\*.so) && FILE=$(echo $PACK | awk -F '/' '{print $NF}') ln -s $PACK /usr/lib/logdata-anomaly-miner/$FILE


# Prepare Supervisord
COPY scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir /var/lib/supervisor && chown $UID.$GID -R /var/lib/supervisor \
    && chown $UID.$GID -R /var/log/supervisor/

USER aminer
WORKDIR /home/aminer

# The following volumes can be mounted
VOLUME ["/etc/aminer","/var/lib/aminer","/logs"]

ENTRYPOINT ["/aminerwrapper.sh"]

# Default command for the ENTRYPOINT(wrapper)
CMD ["aminer","--config","/etc/aminer/config.yml"]
