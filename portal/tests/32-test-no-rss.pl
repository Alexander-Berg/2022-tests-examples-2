#!/usr/bin/perl

use Test::More qw(no_plan);

#freeze time
our $time;

BEGIN {
    our $time = time();
#    *CORE::GLOBAL::time = sub {
#        return $time;
#    };
}

use common;
use strict;
use warnings;

use lib::abs qw( ../scripts/ );
require 'widgets_job.pl';

use POSIX;

use Jobs::test_no_rss;

#mail trys counter
my $mail_sub     = \&WADM::WidgetMailer::mailit;
my $mail_counter = 0;
*WADM::WidgetMailer::mailit = sub {
    $mail_counter++;
    &$mail_sub(@_);
};

sub allmost_now {
    my $come = shift;
    my $diff = time - $come;
    return 1 if ($diff < 4 and $diff >= 0);
    return 0;
}

#ok( time() );
#sleep(1);
#is( time(), $time , 'time freezed '. $time);

ok(Jobs::test_no_rss::init(), 'config inited');
ok(Jobs::test_no_rss::add_block_for(10000));
ok(Jobs::test_no_rss::get_block(10000));
my $a = Jobs::test_no_rss::get_block(10000);
ok(Jobs::test_no_rss::add_block_for(10000));
is($a, Jobs::test_no_rss::get_block(10000), 'block not checnges');

ok(Jobs::test_no_rss::process($a));

my $wid = 26833;

subtest "PREPARE Programs" => sub {
    plan tests => 3;
    my $w = get($wid);
    $w->no_rss(0);
    $w->no_rss_ts('');
    $w->autostatus({});
    add_to_catalog($w);
    $w = get($wid);
    is($w->catflag(), 'inside', 'In catalog');
    is($w->no_rss(),  0,        'rss ok');
    Jobs::test_no_rss::forget($wid);
    is(Jobs::test_no_rss::get_block($wid), undef);
};

ok(Jobs::test_no_rss::add_block_for($wid));
my $b = Jobs::test_no_rss::get_block($wid);
ok($b);
ok(Jobs::test_no_rss::process($b));

my $function_back_up = \&WADM::Monitoring::test_widget_rss;

subtest "FAIL TEST" => sub {
    plan tests => 19;
    my $b = Jobs::test_no_rss::get_block($wid);
    my $w = get($wid);

    save($w);
    *WADM::Monitoring::test_widget_rss = sub {
        my $w = shift;
        #$w->no_rss( 1 ) if( $w );
        return {
            status       => 1,
            info         => 'mock function',
            rss_entries  => 0,
            last_post_ts => time() - 10000
        };
    };

    ok(WADM::Monitoring::test_widget_rss());

    $b->{last_offline} = 0;
    $b->{history}      = [];

    $mail_counter = 0;

    ok(Jobs::test_no_rss::process($b));
    isnt($b->{last_offline}, 0);
    $w = undef;
    $w = get($wid);
    is($w->no_rss(), 1, 'no rss writed ');
    ok(allmost_now($w->no_rss_ts()), 'ts ok');
    is($mail_counter, 0, 'mail not send');
    #hack alter offline time
    $w->no_rss_ts(time() - 50 * 3600);
    save($w);

    isnt(scalar @{$b->{history}}, 0, 'history record added');

    #add
    $b->{first_offline} = 0;
    $mail_counter = 0;
    ok(Jobs::test_no_rss::process($b));
    is($mail_counter, 1, 'mail send');
    # offline to loong, will send mails
    $w = undef;
    $w = get($wid);

    ok($w->autostatus());
    ok(($w->autostatus() and $w->autostatus()->{dontwork}->{norss}), 'auto flag raised');
    ok($w->dont_work(),        'dont work ');
    ok($w->dont_work_reason(), 'dont work ');
    ok(($w->dont_work_complex() and $w->dont_work_complex()->{reason}->{norss}), 'dont work for no rss setted');

    is($w->catflag(),                                'outside', 'removed from catalog');
    is($w->in_catalog(),                             0,         'not in catalog');
    is($w->autostatus()->{excluded_from}->{catalog}, 1,         'Will be restorred');

    $mail_counter = 0;
    ok(Jobs::test_no_rss::process($b));
    is($mail_counter, 0, 'mail not send twice');
};
subtest "SUCESS TEST" => sub {
    plan tests => 14;

    my $w = get($wid);
    $w->no_rss(1);
    save($w);
    *WADM::Monitoring::test_widget_rss = sub {
        my $w = shift;
        #$w->no_rss( 0 ) if( $w );
        return {
            status       => 1,
            info         => 'mock function',
            rss_entries  => 1,
            last_post_ts => time() - 10000
        };
    };
    ok(WADM::Monitoring::test_widget_rss());

    ok($w->autostatus()->{dontwork}->{norss}, 'auto flag raised');
    $mail_counter = 0;
    ok(Jobs::test_no_rss::process($b));
    is($mail_counter, 1, 'mail send');
    $w = undef;
    $w = get($wid);
    is($w->no_rss(), 0, 'no rss writed ');
    ok($w->no_rss_ts(), '');
    isnt(scalar @{$b->{history}}, 0, 'history record added');

    is($w->dont_work(),                       0,     'Works');
    is($w->autostatus()->{dontwork}->{norss}, undef, 'auto status lowered');

    is($w->catflag(),                                'inside', 'added to catalog');
    is($w->in_catalog(),                             1,        'in catalog');
    is($w->autostatus()->{excluded_from}->{catalog}, undef,    'Will be restorred');
    $mail_counter = 0;
    ok(Jobs::test_no_rss::process($b));
    is($mail_counter, 0, 'mail not send twice');
};
my $w = get($wid);
ok($w);
is(Jobs::test_no_rss::test_access(), 1, 'access ok');
ok(Jobs::test_no_rss::add_widget_to_no_rss_monitorig($w));

#exclude include
