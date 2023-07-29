#!/usr/bin/env bash

pkill xfconfd || true
xfce4-panel -q || true

rm -fr ~/.config/xfce4
rm -fr ~/.config/Thunar

cp -ar /etc/xdg/pardus/xfce4  ~/.config/
cp -ar /etc/xdg/pardus/Thunar  ~/.config/

for channel in $(xfconf-query -l | grep -v ':' | tr -d "[:blank:]")
do
    for property in $(xfconf-query -l -c $channel)
    do
        xfconf-query -c $channel -r -p $property || true
    done
done

xfce4-panel &
