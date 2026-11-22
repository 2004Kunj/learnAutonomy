#!/usr/bin/perl
# Anatomy Lab local server for macOS: serves the app folder on 127.0.0.1 using only Perl, which ships with macOS.
# Quits by itself after 4 hours with no requests.
use strict; use warnings; use IO::Socket::INET; use IO::Select;
my ($root, $port) = @ARGV; $root =~ s{/+$}{};
$SIG{PIPE} = 'IGNORE';
my $srv = IO::Socket::INET->new(LocalAddr => '127.0.0.1', LocalPort => $port, Listen => 32, ReuseAddr => 1, Proto => 'tcp') or die "Port $port is busy\n";
my $sel = IO::Select->new($srv);
my %type = (html => 'text/html; charset=utf-8', js => 'application/javascript; charset=utf-8', mjs => 'application/javascript; charset=utf-8',
  json => 'application/json; charset=utf-8', txt => 'text/plain; charset=utf-8', md => 'text/plain; charset=utf-8', css => 'text/css; charset=utf-8',
  png => 'image/png', jpg => 'image/jpeg', svg => 'image/svg+xml', ico => 'image/x-icon', icns => 'image/icns', wasm => 'application/wasm');
while (1) {
  my @ready = $sel->can_read(4 * 3600); exit 0 unless @ready;
  my $c = $srv->accept or next; binmode $c;
  eval {
    local $SIG{ALRM} = sub { die "timeout\n" }; alarm 20;
    my $req = <$c>; die "empty\n" unless defined $req;
    while (my $h = <$c>) { last if $h =~ /^\r?\n$/ }
    alarm 0;
    my ($m, $u) = $req =~ m{^(GET|HEAD)\s+(\S+)};
    my $path = '';
    if ($m) { $u =~ s/[?#].*//; $u =~ s/%([0-9A-Fa-f]{2})/chr hex $1/ge; $u = '/index.html' if $u eq '/'; $path = $root . $u }
    if (!$m || $u =~ m{(^|/)\.\.(/|$)} || $u =~ /\0/ || !-f $path) {
      print $c "HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 9\r\nConnection: close\r\n\r\nNot found";
    } else {
      my ($ext) = $path =~ /\.([A-Za-z0-9]+)$/; my $ct = $type{lc($ext // '')} // 'application/octet-stream';
      open(my $f, '<:raw', $path) or die "open\n"; my $size = -s $f;
      print $c "HTTP/1.0 200 OK\r\nContent-Type: $ct\r\nContent-Length: $size\r\nCache-Control: no-cache\r\nConnection: close\r\n\r\n";
      if ($m eq 'GET') { my $buf; while (read($f, $buf, 262144)) { print $c $buf or last } }
      close $f;
    }
  };
  alarm 0; close $c;
}
