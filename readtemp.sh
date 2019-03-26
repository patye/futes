#!/bin/bash

sudo modprobe w1-gpio
sudo modprobe w1-therm

printf "Külső:        "
cat /sys/bus/w1/devices/28-000002cc42b9/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4
printf "Kazán kilépő: "
cat /sys/bus/w1/devices/28-000002cc5842/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4

printf "*****\n$(date '+%Y-%m-%d %H:%M:%S')\n"  
printf "Fűtés előre:  "
cat /sys/bus/w1/devices/28-00000724371b/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4
printf "Fűtés vissza: "
cat /sys/bus/w1/devices/28-00000723b2b2/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4
printf "Puffer1:      "
cat /sys/bus/w1/devices/28-0000064ff9ea/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4
printf "Puffer2:      "
cat /sys/bus/w1/devices/28-0000072411c1/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4
printf "Puffer3:      "
cat /sys/bus/w1/devices/28-000002cc42b9/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4
printf "Puffer4:      "
cat /sys/bus/w1/devices/28-0000063759a7/w1_slave | tail -1  | awk '{print  $10}' | cut -c3-4
printf "\n\n\n"
