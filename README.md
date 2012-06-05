blpy
====

A small python script for downloading different blocklists, merging them to
"meta" blocklists and hosting them on the local machine.

It uses Python 2.7 with Twisted, so you need that.

I programmed it to be lazy, so it should fetch all blacklists on the first
request and saves them into the ram for the following requests.

It should be fast, after all blacklists are within the ram, but it is not very
optimized on memory usage. (Blacklists are stored within the ram twice, gziped
and as plain text.)

What is this for?
-----------------

Personally I use this for the bittorrent-client "Transmission", but maybe it can
be used for other things too.

Configuration
-------------

Configure blpy by editing the `config.cfg` file.

Running blpy
------------

Run blpy by executing `main.py` with your python interpreter. The first argument
should be the path to your configuration file.

Known Bugs
----------

I tried to save the blacklists persistent on the disk after exit, but this
doesn't work very well at the moment. I think there are difficulties with open
connections. Maybe "Twisted"s ressource objects are not very good pickable.
So the next step is to try split the twisted ressources and the blacklist data.


