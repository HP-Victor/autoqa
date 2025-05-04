FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y     xfce4     xfce4-goodies     x11vnc     xvfb     xdotool     imagemagick     x11-apps     sudo     software-properties-common     imagemagick  && apt-get remove -y light-locker xfce4-screensaver xfce4-power-manager || true  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:mozillateam/ppa  && apt-get update  && apt-get install -y --no-install-recommends firefox-esr  && update-alternatives --set x-www-browser /usr/bin/firefox-esr  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash myuser     && echo "myuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER myuser
WORKDIR /home/myuser

RUN x11vnc -storepasswd secret /home/myuser/.vncpass
RUN mkdir -p /home/myuser/logs

EXPOSE 5900
CMD ["/bin/sh", "-c", "\
    Xvfb :99 -screen 0 1280x800x24 > /home/myuser/logs/xvfb.log 2>&1 & \
    sleep 2 && \
    x11vnc -display :99 -forever -rfbauth /home/myuser/.vncpass -listen 0.0.0.0 -rfbport 5900 > /home/myuser/logs/x11vnc.log 2>&1 & \
    export DISPLAY=:99 && \
    startxfce4 > /home/myuser/logs/xfce4.log 2>&1 & \
    sleep 2 && echo 'Container running!' && \
    tail -f /home/myuser/logs/*.log"]