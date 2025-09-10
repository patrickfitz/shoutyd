![](./static/shoutyd.png)  SHOUTYD
====

## Shouting out our improvements since 2025.

ShoutyD is a lightweight system service that runs at login to inform the user of the changes made by the most recent update. It uses WebUI to call the system browser, and displays an index.html file stored and updated locally. Optionally this html file can call a web based resource for up-to-date information - such as future updates. 
(This is probably should be the default behaviour going forward.)

### Why do we need this?
After looking at the ```opensuse-welcome``` app for some time, it occurred to me that I had no idea what official changes were happening to my OS; I'd dumbly run ```zypper dup``` because, well, it was about time I did. 

I'd hear about new apps being released - elsewhere - by GNOME, or whatever, and wonder if it applied to my system.

ShoutyD (SHOUTYD!!) enables distributions to shout out their changes to their uses - promoting new applications and features. 

In addition it gives users a reason to upgrade - if I was notified that Gnome Image Viewer had been massively updated, I'd go ahead and run an update ASAP. Similarly if there was a security update available, I'd do the same thing.

So it is, in essence, a publicity tool - highlighting the improvements being made over time, and hopefully engaging users more.

### But wait, there's more: 
ShoutyD has an *option* to upload a hardware description to a centralised database. Obviously this hardware description file (currently XML generated from ```lshw```) is anonymised. No user specific information is included, and the serial numbers and UUIDs are hashed.

Why is this important? Telemetry of this type essential for a number of reasons:

* it provides a hardware database against which hardware bugs can be traced
* this database will enable a better understanding of functional hardware - such as memory, cpu, disk and age
* this database can be used to aid decision making by the end user: for example what printer to buy?
* optionally it could be triggered upon boot to update upon discovery of new hardware
* in corporate scenarios it is important to keep track of the hardware estate
* show's who is running what and where

The database location can be changed - currently is it set to https://shoutydb.geekos.org: if can be fixed to any other location - such as a corporate LAN. 

### About the app
As it uses python and WebUI, it should be cross-desktop (possibly even cross platform) - as WebUI simply calls the default browser of the system, which then loads the local html file.

It runs upon user login, and can be silenced if the user is not interested.

### The Web Components: "Babik"
As a long time Django programmer, I decided to implement a lightweight template system to make it easier for others to make changes. 
I've called it "Babik", and I'm likely to turn it into it's own project. Babik aims to a plug-in architecture like Django, but be much smaller and better suited to local web applications. 
It should be a natural fit with WebUI for example. 
The default startup message is currently in markdown format - making it even simpler to author.

### Desktop Integration
As there are native desktop components, is should work seamlessly with any Linux Desktop environment that has a modern web browser installed.

### MORE TO COME!!
* web notifications to start the app
* modular mini-apps - similar in style do Django - that can be easily added, to for example, auto add buttons to provide extra services 
* plus a lot more that I haven't thought of yet ;)

### But the colors scheme is terrible!
* feel free to correct it for your favourite distribution

---
* Copyright (C) Patrick Fitzgerald
* Donated by the Geeko Foundation
* icon found at https://iconduck.com/emojis/16578/cheering-megaphone
# shoutyd
