#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
#--------------------------
#we  just testing mail mode
#----------

use WADM::Mailer;
use Pfile;
use utf8;
#WADM::Mailer;

#load widget
#
require WADM::Index;
use WADM::History;
use WADM::Conf;
#require WADM::Localization;

my $file = WADM::Conf->get('AdminkaLogFile');
ok($file, 'file name obtained from config');

my $dumpInput = {
    Auth => {
        INFO => {
            login => 'test-login',
        },
    },
};

#y $widget = WBOX::Model::Widget->new();
my $widget = WADM::Index::widget_by_wid(222);

ok($widget, 'Dump widget created');
my $o_widget = Storable::dclone($widget);

$widget->yandex(1);
$widget->rating_factors({'rtf_0001' => 1, 'rtf_002' => 0, 'rtf_0003' => 2});

use Hash::Diff qw( diff );
#warn Dumper( diff( $o_widget->get(), $widget->get() ) );

ok(Pfile::POpen($file), 'file can be opend');
ok(
    WADM::History::LogAction(
        $dumpInput,
        'test-action-dumper',
        $o_widget, {
            wdata => $widget->get(),
        }
      )
);
ok(
    WADM::History::LogAction(
        $dumpInput,
        'test-action-dumper',
        $widget, {
            hellow  => 'world',
            xxx     => 'русские буквыё',
            regflag => 'rejected',
        }
      )
);

my ($file_name) = WADM::History::GetLogActionFilenames();
ok($file_name, 'file name to save - ok ');

