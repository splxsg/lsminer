#!/bin/bash

cd /home/lsminer/lsminer

sudo apt-get install python3-pip screen -y
sudo pip3 install cffi

sudo chmod a+x /home/lsminer/lsminer/changekey
sudo chmod a+x /home/lsminer/lsminer/client.py
sudo chmod a+x /home/lsminer/lsminer/update.py
sudo chmod a+x /home/lsminer/lsminer/redline.py
sudo chmod a+x /home/lsminer/lsminer/tty-share
sudo chmod a+x /home/lsminer/lsminer/boot/run
sudo chmod a+x /home/lsminer/lsminer/boot/miner
sudo chmod a+x /home/lsminer/lsminer/boot/driver
sudo chmod a+x /home/lsminer/lsminer/boot/redline
sudo chmod a+x /home/lsminer/lsminer/boot/ttyshare


sync

echo ""
echo "Lsminer is being configured"
echo ---------------------------
echo ""
echo "Files copying..."
echo ""
cp -f /home/lsminer/lsminer/etc/minerscreen.desktop /home/lsminer/.config/autostart/minerscreen.desktop
#cp -f /home/lsminer/lsminer/etc/wallpaper.jpg /home/lsminer/wallpaper.jpg
sudo cp -f /home/lsminer/lsminer/etc/prepare.service /etc/systemd/system/prepare.service
sudo cp -f /home/lsminer/lsminer/etc/miner.service /etc/systemd/system/miner.service
sudo cp -f /home/lsminer/lsminer/etc/redline.service /etc/systemd/system/redline.service
sudo cp -f /home/lsminer/lsminer/etc/ttyshare.service /etc/systemd/system/ttyshare.service
sudo cp -f /home/lsminer/lsminer/etc/screenrc /etc/screenrc
sudo cp -f /home/lsminer/lsminer/etc/lsminer.conf /home/lsminer/lsminer.conf
sync
sleep 1

sudo systemctl daemon-reload

echo "Activating services..."
echo ""
[ -f /etc/systemd/system/prepare.service ] && echo "Service loaded: prepare" && systemctl enable prepare
[ -f /etc/systemd/system/miner.service ] && echo "Service loaded: miner" && systemctl enable miner
[ -f /etc/systemd/system/redline.service ] && echo "Service loaded: redline" && systemctl enable redline
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