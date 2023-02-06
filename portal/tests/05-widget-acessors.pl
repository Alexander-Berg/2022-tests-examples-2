#!/usr/bin/perl

use Test::More qw(no_plan);

use strict;

use common;
#--------------------------
#we  just testing mail mode
#----------

use WADM::Mailer;
use utf8;
#WADM::Mailer;

#load widget
#
require WADM::Index;
use WBOX::Model::Widget;

#require WADM::Localization;

my $widget = WBOX::Model::Widget->new();
ok($widget,                            'widget inited');
ok($widget->make_accessor('AutoTest'), '->Auto Test created');

ok($widget->can('site'),    'Site function ok');
ok($widget->site('www.ru'), 'Site set works');
is(
    $widget->site(), q{www.ru}
    , 'Www.ru seted'
);

is(
    $widget->site('abc'), q{abc}
    , 'site setted'
);
is(
    $widget->{__SITE}, q{abc}
    , ' Hash param ok'
);
is(
    $widget->{__BIN}, undef
    , 'Bin undef yet'
);

ok($widget->get(),   'Get created bin');
ok($widget->{__BIN}, 'Bin inited');
is(
    $widget->site('bc'), q{bc}
    , 'site setted'
);
is(
    $widget->{__BIN}->{__SITE}, q{bc}
    , 'Bin param ok'
);

$widget = WBOX::Model::Widget->new({
        raw => {
            wdata => {
                __WARNING_DT       => '2004-02-01 01:01:01',
                __SITE             => 'yandex.ru',
                __SITE_KARMA       => 4,
                __CATREJECT_REASON => 'YES',
                __SITE_CI          => 160,

            },
            warning_dt => '0000-00-00 00:00:00',
            banned_dt  => '2010-01-01 01:01:00',
            deleted_dt => '2010-02-02 02:02:00',
            #        bad_response=> 2,
          }
    }
);
ok($widget, 'widget ReiNited');
is(
    $widget->warning_dt, ''
    , 'Wrning Dt ok'
);
is(
    $widget->site(), 'yandex.ru'
    , 'site ok'
);
#is( $widget->site_ci(),160  , 'site_ci ok');
#is( $widget->site_karma, 4  , 'site karma is ok');
is(
    $widget->catreject_reason, q{YES}
    , 'cat rejects ok'
);

is($widget->titleurl_available(), 1, 'title url by default');
is($widget->titleurl_available(0), 0);
is($widget->titleurl_failed_ts(), time(), 'title url failed ok!');

#is( $widget->bad_response(   )      , ''     , 'bad response off by default');

is($widget->src_available(), 1, 'srv available by default');
is($widget->src_available(0), 0);
is($widget->src_failed_ts(), time(), 'src failed ok');

ok($widget->src_available(1));
ok($widget->titleurl_available(1));
is($widget->src_failed_ts(),      '', 'src url recovered ok!');
is($widget->titleurl_failed_ts(), '', 'title url recovered ok!');

is($widget->banned_dt(),  '2010-01-01 01:01:00', 'Banned dt loaded');
is($widget->deleted_dt(), '2010-02-02 02:02:00', 'deleted dt loaded');

ok($widget->actflag('active'));
is($widget->actflag(),    'active', 'widget activatiedr');
is($widget->banned_dt(),  '',       'banned dt dropped');
is($widget->deleted_dt(), '',       'delete dt dropped');

ok($widget->catflag('request'));
ok($widget->catalog_request_dt());
ok($widget->catflag('inside'));
ok($widget->in_catalog(), 'In catalog');
#is( $widget->catalog_request_dt(), ''); #don drop now
ok($widget->catflag('reject'));
is($widget->in_catalog(), 0);

ok($widget->regflag('request'));
ok($widget->regional_request_dt());
ok($widget->regflag('inside'));
ok($widget->in_regional(), 'In regional');
#is( $widget->regional_request_dt(), ''); #dont drop now
ok($widget->regflag('reject'));
is($widget->in_regional(), 0);
#is( $widget->regional_request_dt(), '' ); #dont drop now?
#is( $widget->bad_response() , 2);

SKIP: {
    skip 'bad responnce not available in trunk', 1;
    is($widget->bad_response(1), 1);
}

ok(1,                                 '!!');
ok($widget->catflag('outside'),       'make it outside');
ok($widget->warning_reason(' Kill '), 'set warning');
ok($widget->warning_dt(POSIX::strftime("%F %T", localtime())), 'Set Time');

#warning_complex
#$widget->warning_complex( '' );
ok($widget->warning_recalculate({}), 'drop warnings');
is($widget->warning_reason(), '', 'NO reason');
is($widget->warning_dt(),     '', 'NO DT');
ok($widget->warning_add('test-a', 'texta'));
ok($widget->warning_reason(), 'reason');
ok($widget->warning_dt(),     'DT');
ok($widget->warning_add('test-b', 'textb'));
is($widget->warning_reason(), "texta\ntextb", 'text is fulli correct');

$widget->warning_complex()->{td}->{'test-b'} = 20010;

ok($widget->warning_recalculate($widget->warning_complex()), 'drop warnings');

is($widget->warning_dt(), '1970-01-01 08:33:30', 'DT is minimal');

$widget->warning_drop('test-a');
is($widget->warning_reason(), "textb", 'text is fulli correct');
ok($widget->warning_drop('test-b'));
#warn Dumper( $widget->warning_complex() );
is($widget->warning_complex(), '');
is($widget->warning_reason(),  '', 'NO reason');
is($widget->warning_dt(),      '', 'NO DT');

#dont_work_complex
#$widget->dont_work_complex( '' );
ok($widget->dont_work_recalculate({}), 'drop dont_works');
is($widget->dont_work_reason(), '', 'NO reason');
is($widget->dont_work_dt(),     '', 'NO DT');
ok($widget->dont_work_add('test-a', 'texta'));
ok($widget->dont_work_reason(), 'reason');
ok($widget->dont_work_dt(),     'DT');
ok($widget->dont_work_add('test-b', 'textb'));
is($widget->dont_work_reason(), "texta\ntextb", 'text is fulli correct');

$widget->dont_work_complex()->{td}->{'test-b'} = 20010;

ok($widget->dont_work_recalculate($widget->dont_work_complex()), 'drop dont_works');

is($widget->dont_work_dt(), '1970-01-01 08:33:30', 'DT is minimal');

$widget->dont_work_drop('test-a');
is($widget->dont_work_reason(), "textb", 'text is fulli correct');
ok($widget->dont_work_drop('test-b'));
#warn Dumper( $widget->dont_work_complex() );
is($widget->dont_work_complex(), '');
is($widget->dont_work_reason(),  '', 'NO reason');
is($widget->dont_work_dt(),      '', 'NO DT');

ok($widget->author_name('mike'));
is($widget->author_name(), 'mike', 'author name ok');

ok($widget->author_email('mike@ya.ru'));
is($widget->author_email(), 'mike@ya.ru', 'author email ok');

