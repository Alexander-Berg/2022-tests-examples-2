package MordaX::Pumpkin::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use MP::Logit qw(dmp);

use Test::Most;
use MordaX::Req;
use Scalar::Util qw(weaken);
use Scope::Guard qw(guard);
use MordaX::FcgiRequest;
use MordaX::Pumpkin;

sub req {
    my $r   = MordaX::FcgiRequest->new();
    my $req = MordaX::Req->new();

    return MordaX::Req->new(
        'r'   => $r,
        'req' => $req
    );
}

sub r {
    return MordaX::FcgiRequest->new();
}

sub logit_capture {
    my $self = shift;
    weaken(my $ret = shift);
    my $real_logit = \&MordaX::Pumpkin::logit;
    no warnings 'redefine';
    *MordaX::Pumpkin::logit = sub { $ret->{ $_[0] }++ };
    return guard {
        no warnings 'redefine';
        *MordaX::Pumpkin::logit = $real_logit;
    };
}

sub on : Tests {
    is MordaX::Pumpkin::on({ pumpkin => 1 }), 1;
    is MordaX::Pumpkin::on({}), 0;
}

sub detect : Tests {
    my $self = shift;
    # writing errors
    {
        no warnings qw(redefine);
        my $errors = {};
        my $guard  = $self->logit_capture($errors);

        my $req = {};
        MordaX::Pumpkin::detect({}, {});
        is $req->{pumpkin}, undef;
    }
    # sandbox ok, headers not ok
    {
        my $req = $self->req;
        my $nets = $MordaX::Nets::nets;
        $nets->addnetwork('internal_production', qw(2a02:6b8:0:1a19::/64));

        my $r = $self->r();
        $r->_set_xri('2a02:6b8:0:1a19:feaa:14ff:fe1d:f7c6');
        my $headers       = MP::HTTP::Headers->new();
        $r->{'_HEADERS'} = $headers;

        MordaX::Pumpkin::detect($r, $req);
        is MordaX::Pumpkin::on($req), 0;
    }
    # sandbox ok, headers ok
    {
        my $req = $self->req;
        my $nets = $MordaX::Nets::nets;
        $nets->addnetwork('internal_production', qw(2a02:6b8:0:1a19::/64));

        my $r = $self->r();
        $r->_set_xri('2a02:6b8:0:1a19:feaa:14ff:fe1d:f7c6');
        my $headers       = MP::HTTP::Headers->new();
        $headers->header('X-Yandex-Morda-Pumpkin' => 1);
        $r->{'_HEADERS'} = $headers;

        MordaX::Pumpkin::detect($r, $req);
        is MordaX::Pumpkin::on($req), 1;
    }
    # sandbox not ok, headers ok
    {
        my $req = $self->req;
        my $nets = $MordaX::Nets::nets;
        $nets->addnetwork('internal_production', qw(2a02:6b8:0:1a19::/64));

        my $r = $self->r();
        $r->_set_xri('3a02:6b8:0:1a19:feaa:14ff:fe1d:f7c6');
        my $headers       = MP::HTTP::Headers->new();
        $headers->header('X-Yandex-Morda-Pumpkin' => 1);
        $r->{'_HEADERS'} = $headers;

        MordaX::Pumpkin::detect($r, $req);
        is MordaX::Pumpkin::on($req), 0;
    }
}

sub get_requested_geo : Tests {
    my $self = shift;
    {

        my $req = $self->req;
        is MordaX::Pumpkin::get_requested_geo($req), undef;
    }
    {
        my $req = $self->req;
        $req->{UserHeaders}->{'X-Yandex-Morda-Pumpkin-Geo'} = 65;
        is MordaX::Pumpkin::get_requested_geo($req), 65;
    }
}
1;

