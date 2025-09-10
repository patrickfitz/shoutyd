### But wait, there's more: 
ShoutyD will shortly have an *option* to upload a hardware description to a centralised database. Obviously this hardware description file (currently XML generated from ```lshw```) is anonymised. No user specific information is included, and the serial numbers and UUIDs are hashed.

Why is this important? Telemetry of this type essential for a number of reasons:

* it provides a hardware database against which hardware bugs can be traced
* this database will enable a better understanding of functional hardware - such as memory, cpu, disk and age
* this database can be used to aid decision making by the end user: for example what printer to buy?
* optionally it could be triggered upon boot to update upon discovery of new hardware
* in corporate scenarios it is important to keep track of the hardware estate
* show's who is running what and where

The database location can be changed - currently is it set to https://shoutydb.geekos.org: if can be fixed to any other location - such as a corporate LAN. 
