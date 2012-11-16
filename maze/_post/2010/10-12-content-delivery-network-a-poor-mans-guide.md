---
title: Content Delivery Network: a poor man's guide
---
So, keeping up with the latest buzz, I started wondering how I could set up my
own CDN, or
[Content Delivery Network](http://en.wikipedia.org/wiki/Content_delivery_network).
Virtual Private Servers, or VPS, are getting cheaper every time, starting at an
average rate of $5 for an entry-level server.

Looking at the tools and techniques at hand, I implemented a small proof of
concept CDN using PowerDNS and <s>nginx</s> lighttpd. Lighttpd is the <s>new
buzz</s> reliable web server with a small memory-footprint for serving static
content at ridiculously fast rated by implementing techniques like
[sendfile](http://linux.die.net/man/2/sendfile), by tying together the socket
and file descriptors. As you may know, Linux is pretty good at building up a
file cache in memory, so getting a VPS with at least 128MB memory is a good
start.

For this demo, I decided to use a VPS from <s>XLS Hosting</s> [Cloud
VPS](http://www.cloudvps.nl/) located in The Netherlands, and one at VPS Tree
located in the United States. Both servers are equipped with 128MB of RAM,
Ubuntu Lucid 10.04 LTS.

## Installing the required software

Firstly, you will have to install the required software on both of your servers:

    :::bash
    maze@vps$ sudo apt-get install pdns-server pdns-backend-geo lighttpd rsync
    ...

That's it, now continue configuring.

## Configuring your DNS

For this setup I am using ns0.net.maze.io and ns4.net.maze.io for my setup. ns0
points to the VPS located in The Netherlands, ns4 points to the United States.

## Configuring geo-based DNS

The folks at [nerd.dk](http://countries.nerd.dk/) are providing a DNS-based
blacklist (DNSBL) which allows you to estimate a country based on network
prefix. This list is pretty accurate, the only disadvantage to this approach is
that it rules out sites using [anycast](http://en.wikipedia.org/wiki/Anycast).
You could also set up a geo-DNS using
[GeoIP](http://www.maxmind.com/app/ip-location) and a custom PowerDNS backend
to offer more reliable location predictions, but this also comes at a cost by
having more latency.

The PowerDNS [geo backend](http://doc.powerdns.com/geo.html) offers a way to
load a [rbldns](http://cr.yp.to/djbdns/rbldns.html)-formatted zone file into
memory. Let's start configuring.

Firstly, create the required directories:

    :::bash
    maze@vps$ mkdir -p /etc/powerdns/countries
    maze@vps$ mkdir -p /etc/powerdns/geo-maps

Now we download the latest zz.countries.nerd.dk rbldnsd zone file, for more
information on this file [read this](http://countries.nerd.dk/more.html):

    :::bash
    maze@vps$ rsync -qt rsync://countries-ns.mdc.dk/zone/zz.countries.nerd.dk.rbldnsd \
        /etc/powerdns/countries/

Next, let us configure PowerDNS' geo backend. A few assumptions:
<blockquote>
<ul class="simple">
    <li>The DNS record I want to act as my content delivery network is <tt class="docutils literal"><span class="pre">cdn.maze.io</span></tt></li>
    <li>The DNS servers I will be using for PowerDNS' geo backend, are <tt class="docutils literal"><span class="pre">ns0.net.maze.io</span></tt> and <tt class="docutils literal"><span class="pre">ns4.net.maze.io</span></tt></li>
</ul>
</blockquote>
Configure the backend:

    :::bash
    maze@vps$ cat > /etc/powerdns/pdns.d/pdns.local.geo <<EOF
    # geo Configuration
    #
    # See for more information /usr/share/doc/pdns-backend-geo/README
    #
    geo-zone=cdn.maze.io
    geo-soa-values=ns0.net.maze.io,systems.maze.io
    geo-ns-records=ns0.net.maze.io,ns1.net.maze.io
    geo-ttl=60
    geo-ns-ttl=3600
    geo-ip-map-zonefile=/etc/powerdns/countries/zz.countries.nerd.dk.rbldnsd
    geo-maps=/etc/powerdns/geo-maps

Great, now we can start setting up (sub)domains in the <tt class="docutils
literal"><span class="pre">cdn.maze.io</span></tt> zone. This is what the
directory <tt class="docutils literal"><span
class="pre">/etc/powerdns/geo-maps</span></tt> is for. Each file in here
represents a (sub)domain within the configured <tt class="docutils
literal"><span class="pre">geo-zone</span></tt>. The zone uses <a
class="reference"
href="http://en.wikipedia.org/wiki/ISO_3166-1_numeric#Officially_assigned_code_elements">ISO
3166 numeric</a> notation:

    :::bash
    maze@vps$ cat > /etc/powerdns/geo-maps/cdn.maze.io
    $RECORD cdn.maze.io.
    $ORIGIN cdn.maze.io.
    # Default
    0       eu
    # The Netherlands
    528     eu
    # United States
    840     us

You can download the complete zone from <a class="reference"
href="http://cdn.maze.io/examples/dns/cdn.maze.io.zone">http://cdn.maze.io/examples/dns/cdn.maze.io.zone</a>
with all current ISO 3166-2 country codes assigned to the continents. You can
generate this zone contents yourself using the iso2region script by David
Leadbeater (<a class="reference"
href="http://www.google.com/search?q=iso2region.pl">google</a>). It is
important to assign special numeric value <tt class="docutils literal"><span
class="pre">0</span></tt> to a continent manually, as this serves as a
fallback.

## Start your engines!

Now we are ready to fire up PowerDNS, it should mention the newly added backend
and its zones upon start (see <tt class="docutils literal"><span
class="pre">/var/log/daemon.log</span></tt> in Ubuntu). If you wish to reload
further changes, use the <tt class="docutils literal"><span
class="pre">pdns_control</span> <span class="pre">rediscover</span></tt>
command:

    :::log
    Oct 12 21:18:14 vps1 pdns[19959]: [GeoBackend] This is the geobackend (Jan 13 2010, 19:19:25 -
        $Revision: 1.1 $) reporting
    Oct 12 21:18:15 vps1 pdns[19959]: [geobackend] Parsing IP map zonefile
    Oct 12 21:18:15 vps1 pdns[19959]: [geobackend] Finished parsing IP map zonefile: added 104173 prefixes,
        stored in 259330 nodes using 6223920 bytes of memory
    Oct 12 21:18:15 vps1 pdns[19959]: [geobackend] Parsing director map /etc/powerdns/geo-maps/cdn.maze.io
    Oct 12 21:18:15 vps1 pdns[19959]: [geobackend] Finished parsing 1 director map files, 0 failures

Let's start asking the backend some questions:

    :::bash
    maze@vps-usa$ dig cdn.maze.io @127.0.0.1

    ; <<>> DiG 9.7.0-P1 <<>> cdn.maze.io @127.0.0.1
    ;; global options: +cmd
    ;; Got answer:
    ;; ->>HEADER<<- opcode: QUERY, status: SERVFAIL, id: 45536
    ;; flags: qr rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0
    ;; WARNING: recursion requested but not available

    ;; QUESTION SECTION:
    ;cdn.maze.io.                   IN      A

    ;; ANSWER SECTION:
    cdn.maze.io.            60      IN      CNAME   eu.local.maze.io.

    ;; Query time: 0 msec
    ;; SERVER: 127.0.0.1#53(127.0.0.1)
    ;; WHEN: Wed Oct 13 00:21:45 2010
    ;; MSG SIZE  rcvd: 52

That's odd, this server is located in the United Stated, so this must be the
fallback giving a reply! Let's try our external interface:

    :::bash
    maze@vps-usa$ dig cdn.maze.io @ns4.net.maze.io

    ; <<>> DiG 9.7.0-P1 <<>> cdn.maze.io @ns4.net.maze.io
    ;; global options: +cmd
    ;; Got answer:
    ;; ->>HEADER<<- opcode: QUERY, status: SERVFAIL, id: 53774
    ;; flags: qr rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0
    ;; WARNING: recursion requested but not available

    ;; QUESTION SECTION:
    ;cdn.maze.io.                   IN      A

    ;; ANSWER SECTION:
    cdn.maze.io.            60      IN      CNAME   us.local.maze.io.

    ;; Query time: 1 msec
    ;; SERVER: 66.197.179.116#53(66.197.179.116)
    ;; WHEN: Wed Oct 13 00:22:37 2010
    ;; MSG SIZE  rcvd: 52

That's better, as you can see our backend is working nicely!

## But you said <cite>Content</cite> Delivery!

Ah yes, now let's set up lighttpd to serve out CDN, it's really not exciting:

    :::lighttpd
    $HTTP["host"] =~ "cdn.maze.io" {
        url.rewrite-once = (
            "^/?$" => "http://maze.io/"
        )
        server.document-root = "/var/www/cdn.maze.io"
    }

Now use some rsync kungfu to set up synchronisation of your CDN files and let
the magic happen!
