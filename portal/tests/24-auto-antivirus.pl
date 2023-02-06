#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

use POSIX;
#--------------------------
#we  just testing mail mode
#----------

#WADM::Mailer;

#load widget
#
require WADM::Index;
use WBOX::Model::Widget;
use WADM::Monitoring;
use WADM::History;
use WADM::HistoryController;

use WADM::Auto;

#require MordaX::Errorlog;
#require InitMorda;
use MordaX::Conf;
#use InitUtils;
use MordaX::Data_load;
use MordaX::Blocks;

%MordaX::Blocks::blocks = (
    '__misc_datas__' => {
    },
);

MordaX::Data_load::load_static_exports();

use Data::Dumper;
print Dumper(
    \%MordaX::Data_load::static_exports,
);
my $id = 30713;
my $w  = get($id);
$w->virusflag(0);

save($w);

subtest " init " => sub {
    plan tests => 1;
    my $w = get($id);
    is($w->virusflag(), 0);
};

subtest " SET " => sub {
    plan tests => 6;
    $w = get($id);
    is($w->virusflag(), 0);
    ok($w->virusflag(1));
    is($w->virusflag(), 1);
    ok($w->virusflag(2));
    is($w->virusflag(),  2);
    is($w->virusflag(0), 0);
};

subtest " AUTO " => sub {
    plan tests => 7;
    $w = get($id);

    is($w->virusflag(), 0);

    my $res = WADM::Auto::alter_widget_virusflag(
        widget    => $w,
        virusflag => 1,
        login     => 'autotest',
    );

    is($w->virusflag(), 1, 'VF setted');
#    ok( $res );

    my $res2 = WADM::Auto::alter_widget_virusflag(
        widget    => $w,
        virusflag => 2,
        login     => 'autotest',
    );

    is($w->virusflag(), 2, 'VF setted');

    ok($res2);
    ok($res2->{infected});
    ok($res2->{sendmail});
    ok($res2->{logaction});
};

subtest " FAKEINPUT " => sub {
    plan tests => 6;
    my $fi = FakeInput->new();
    ok($fi);
    my $fil = FakeInput->new(login => 'autotest');
    ok($fil);
    is(ref($fil), 'FakeInput');
    my ($login, $uid) = WADM::History::_get_login_info($fil);
    #print Dumper( $fil );
    is($login, 'autotest', 'Fake input understanded corrctly');

    my ($login2, $uid2) = WADM::History::_get_login_info('nk');
    is($login2, 'nk');
    is($uid2,   0);
};

ok(WADM::Reasons::get_reason_for_widget('virus:found'), 'Reason ok');

subtest " MAIL " => sub {
    plan tests => 1;
    my $res = {
        widget   => $w,
        login    => 'autotest',
        sendmail => {
            action => 'bad_response:clean',
        },
    };

    ok(WADM::Auto::mail_and_log($res));
};

subtest " LOG " => sub {
    plan tests => 2;
    my $res = {
        widget    => $w,
        login     => 'autotest',
        logaction => {
            action => 'AUTO:TEST',
            changes => {'hi ' => rand()},
        },
    };
  TODO: {
        local $TODO = "mail and log return codes not implemented";
        ok(WADM::Auto::mail_and_log($res));
        is(WADM::Auto::mail_and_log(undef), undef, '!');
    }
  }

