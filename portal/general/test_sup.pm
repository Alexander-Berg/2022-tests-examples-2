#!/usr/bin/perl

package test_sup;
use common::sense;
use warnings;
use strict;
use lib::abs qw(../lib);

use Smoo::Notification;
use Smoo::Notification::Sup;
use MP::Logit qw(logit dmp);


sub Smoo::Notification::Sup::_sup_push(+;$) {
    return {
        ok => 1,
        'msg' => 'test mocked',
    };

    dmp( @_ );
}

package Smoo::Notification;
#Smoo::Notification::_transports()->{'Sup'}->{'send'} = \&Smoo::Notification::Sup::send;

1;
