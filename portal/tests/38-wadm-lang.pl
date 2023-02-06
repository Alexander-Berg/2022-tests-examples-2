#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib ../../lib);

#use InitBase;
use WADM::WidgetMailer;

my $file = $ARGV[0];
ok($file,    'FILE in ' . $file);
ok(-f $file, 'file found');

#INTERFACE TEST

my $auto = do($file) || {};
for my $l (qw/ru uk en/) {
    subtest "INTEFACE: $l " => sub {
        ok($auto->{$l}, 'language present');
        for my $if (qw/to_main/) {
            ok($auto->{$l}->{iface}->{$if}, "IFACE $l -> $if presents");
        }
        done_testing();
      }
}

#MAIL TEST
my @mail_languages = keys %WADM::WidgetMailer::mail_available_languages;
ok(scalar @mail_languages, 'mail on other langugages present ');
for my $l (@mail_languages) {    #en
    subtest "MAIL $l " => sub {
        ok($auto->{$l}, 'language present') || return;

        #TEXT
        for my $text (qw/add_on_yandex widget_without_title widget_without_title_for_promo/) {
            ok($auto->{$l}->{text}->{$text}, "$l.text.$text presents");
        }
        #MAIL
        for my $action (qw/actflag:banned
            catflag:avalible catflag:inside catflag:outside catflag:reject
            dont_work dont_work:heavy
            recommendation regflag:inside regflag:outside
            regflag:reject
            rss:recover
            rss:rotten
            rss:warn
            /) {
            ok($auto->{$l}->{mail}->{$action}, "$l.mail.$action presents");
        }
        done_testing();
    };
}

done_testing();

