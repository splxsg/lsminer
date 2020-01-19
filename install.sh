#!/bin/bash

cd /home/lsminer/lsminer

sudo apt-get install xinit xterm python3-pip screen tmux -y

wait && sync && sleep 1

sudo pip3 install cffi

sudo chmod a+x /home/lsminer/lsminer/client.py
sudo chmod a+x /home/lsminer/lsminer/update.py
sudo chmod a+x /home/lsminer/lsminer/lsremote.py
sudo chmod a+x /home/lsminer/lsminer/gpumon.py
sudo chmod a+x /home/lsminer/lsminer/kernel.py
sudo chmod a+x /home/lsminer/lsminer/minerinfo.py
sudo chmod a+x /home/lsminer/lsminer/tools.py
sudo chmod a+x /home/lsminer/lsminer/changekey
sudo chmod a+x /home/lsminer/lsminer/tty-share
sudo chmod a+x /home/lsminer/lsminer/lsminer_rw
sudo chmod a+x /home/lsminer/lsminer/ohgodatool
sudo chmod a+x /home/lsminer/lsminer/overclock
sudo chmod a+x /home/lsminer/lsminer/lsminer_rw
sudo chmod a+x /home/lsminer/lsminer/boot/run
sudo chmod a+x /home/lsminer/lsminer/boot/miner
sudo chmod a+x /home/lsminer/lsminer/boot/driver
sudo chmod a+x /home/lsminer/lsminer/boot/lsremote
sudo chmod a+x /home/lsminer/lsminer/boot/ttyshare
sudo chmod a+x /home/lsminer/lsminer/boot/amdmeminfo
sudo chmod a+x /home/lsminer/lsminer/boot/monitor
sudo chmod a+x /home/lsminer/lsminer/oc/runnvoc

sync

echo ""
echo "Lsminer is being configured"
echo ---------------------------
echo ""
echo "Files copying..."
echo ""
cp -f /home/lsminer/lsminer/etc/tmux.conf /home/lsminer/.tmux.conf
sudo cp -f /home/lsminer/lsminer/etc/prepare.service /etc/systemd/system/prepare.service
sudo cp -f /home/lsminer/lsminer/etc/miner.service /etc/systemd/system/miner.service
sudo cp -f /home/lsminer/lsminer/etc/lsremote.service /etc/systemd/system/lsremote.service
sudo cp -f /home/lsminer/lsminer/etc/ttyshare.service /etc/systemd/system/ttyshare.service
sudo cp -f /home/lsminer/lsminer/etc/screenrc /etc/screenrc
sudo cp -f /home/lsminer/lsminer/etc/lsminer.conf /home/lsminer/lsminer.conf
ln -s /home/lsminer/lsminer/oc/runnvoc /usr/bin/runnvoc
ln -s /home/lsminer/lsminer/lsminer_rw /usr/bin/lsminer_rw

sync
sleep 1

sudo systemctl daemon-reload

echo "Activating services..."
echo ""
[ -f /etc/systemd/system/prepare.service ] && echo "Service loaded: prepare" && systemctl enable prepare
[ -f /etc/systemd/system/miner.service ] && echo "Service loaded: miner" && systemctl enable miner
[ -f /etc/systemd/system/lsremote.service ] && echo "Service loaded: lsremote" && systemctl enable lsremote
[ -f /etc/systemd/system/ttyshare.service ] && echo "Service loaded: ttyshare" && systemctl enable ttyshare

echo "Setting permissions..."
echo ""
sudo chown -R lsminer:lsminer /home/lsminer/*
sudo chown -R root:root /etc/*

echo "Finished!"
echo ---------------------------
echo ">> Please REBOOT to apply changes of new version."
echo ---------------------------
sync
sleep 3
exit 0
