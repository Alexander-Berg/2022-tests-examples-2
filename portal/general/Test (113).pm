package MordaX::YCookie::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use Test::More;

use MordaX::YCookie;
use MordaX::Req;
use MordaX::FcgiRequest;

sub req {
    my $r   = MordaX::FcgiRequest->new();
    my $req = MordaX::Req->new();

    return MordaX::Req->new(
        r   => $r,
        req => $req
    );
}

sub update_sp : Tests(17) {
    my $self = shift;

    my $req = $self->req();
    my $ycookies = MordaX::YCookie->new($req);
    my $other    = MordaX::YCookie->new($req);

    my @tests = (
        [undef,     undef,    undef],

        ['',        undef,    ''],
        ['a',       undef,    'a'],
        ['a:b:c',   undef,    'a:b:c'],

        [undef,     '',       undef],
        [undef,     'a',      undef],
        [undef,     'a:b:c',  undef],

        ['a:b',     undef,   'a:b'],
        ['a:b',     '',      'a:b'],
        ['a:b',     'a',     'a:b'],
        ['a:b',     'a:b:c', 'a:b'],

        [undef,     'a:b',   'a:b'],
        ['',        'a:b',   'a:b'],
        ['a',       'a:b',   'a:b'],
        ['a:b:c',   'a:b',   'a:b'],

        ['a:b:c:d', 'e:f',   'a:b:c:d:e:f'],
        ['a:b:c:d', 'a:x',   'a:x:c:d'],
    );

    for (@tests) {
        my ($sp, $sp_other, $result) = @$_;
        $ycookies->setyp('sp', $sp, $req->{time} + MordaX::YCookie::SP_EXPIRE());
        $other->setyp('sp', $sp_other, $req->{time} + MordaX::YCookie::SP_EXPIRE());
        $ycookies->update_sp($req, $other);
        my $sp_updated = $ycookies->value('sp');
        if (my %sp = MordaX::YCookie::_valid_sp_hash($sp_updated)) {
            my %result = split(':', $result);
            is_deeply(\%sp, \%result);
        }
        else {
            is $sp_updated, $result;
        }
    }
}


1;

