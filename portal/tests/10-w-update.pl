#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

require WADM::Index;
use WBOX::Model::Widget;
use WBOX::Requester;
use WADM::Monitoring;
use WADM::History;
use WADM::Utils;
use POSIX;
use Digest::MD5 qw(md5_hex);

#$WBOX::Requester::requester->{debug} = 1;

my $wi35 = WADM::Index::widget_by_wid(35);
is($wi35->actflag(), 'active', 'Active at start');
ok($wi35->actflag('complained'));
#is( $wi35->stale_rss(), ''          , 'ok' );
#ok( $wi35->stale_rss(1));
my $ts = time - 100000 - int(rand(5000));
$wi35->titleurl_available_ts($ts);
is($wi35->titleurl_available_ts(), $ts);

my $catflag = ($wi35->catflag() eq 'outside' ? 'reject' : 'outside');
my $catreject = rand(100) + 1;
ok($wi35->catflag($catflag));
ok($wi35->catreject_reason($catreject));
my $catalog_dt = strftime('%F %T', localtime(time - rand(5000)));
ok($wi35->catalog_dt($catalog_dt));

my $regional_dt = strftime('%F %T', localtime(time - rand(5000)));
ok($wi35->regional_dt($regional_dt));
ok($wi35->regflag($wi35->regflag() eq 'outside' ? 'reject' : 'outside'));
ok($wi35->regreject_reason(rand(100) + 1));

#ok( $wi35->users( 1 + int(rand (100)))); #ro
#ok( $wi35->rating( 1 + int(rand( 100 )))); #RO
#ok( $wi35->uid( 1 + int( rand(100) ) ));

ok($wi35->alias('test' . int(rand(100))));
ok($wi35->alias(), 'alias setted');
ok($wi35->_setvalue('__TITLE',     'test' . int(rand(100))));
ok($wi35->_setvalue('__TITLE_URL', 'http://test' . int(rand(100)) . '.ru'));
like($wi35->title(), qr{^test});
#like( $wi35->titleurl(), qr{test});
#ok( $wi35->titlehide( 1+ int(rand(100)) ));

#ok( $wi35->create_dt(strftime('%F %T', localtime( time - rand( 5000)))) );

ok($wi35->stale_rss(int(rand(20)) + 1));
ok($wi35->salt(md5_hex(rand)));
ok($wi35->salt_prev(md5_hex(rand)));

ok($wi35->warning_dt(strftime('%F %T', localtime(time - rand(5000)))));
ok($wi35->warning_reason('test' . int(rand(100))));

ok($wi35->banned_dt($regional_dt),  "Set banned dt");
ok($wi35->deleted_dt($regional_dt), 'Set deleted dt');

ok($wi35->catalog_request_dt($regional_dt));
ok($wi35->regional_request_dt($regional_dt));
ok($wi35->in_catalog(1),  'set in catalog');
ok($wi35->in_regional(1), 'set in regional');
#ok( $wi35->bad_response(1), 'bad_responce_on') ;
ok($wi35->title_url('http://mike.ru'), 'title_url set');

ok($wi35->author_email('mike' . int(rand(100)) . '@ya.ru'), 'email');
ok($wi35->author_name('mike' . int(rand(100))),             'name');

ok($wi35->m_counter_id(int(rand(10000))), 'rand in m_counter_id');

#$WBOX::Requester::requester->{debug} = 2;
$WBOX::Requester::requester->widget_update(
    $wi35,
    WADM::Utils::get_master_retry_pattern(),
    #WADM::Conf->get('WboxDBMaster'),
    2
);
#$WBOX::Requester::requester->{debug} = 0;

my $wi35_2 = WADM::Index::widget_by_wid(35);

is($wi35_2->actflag(), 'complained', 'Complained');
#is( $wi35_2->stale_rss()      ,1            , 'Staled' );
#is( $wi35_2->stale_rss(0)     , ''          , 'Stale disabled'    );
is($wi35_2->titleurl_available_ts(), $ts, 'TS ok');

#is( $wi35_2->catflag(), $catflag            , 'catflag');
#is( $wi35_2->catalog_dt(), $catalog_dt      , 'catalog_dt');
#is( $wi35_2->catreject_reason(), $catreject , 'catreject' );
is($wi35_2->regional_dt(), $regional_dt, 'regional_dt');

for (
    qw/
    regional_dt
    regional_request_dt
    regreject_reason
    users rating uid create_dt stale_rss
    titleurl
    titleurl_available_ts
    warning_reason

    warning_dt
    banned_dt
    deleted_dt

    catflag
    catalog_dt
    catalog_request_dt
    catreject_reason

    in_catalog
    in_regional
    title_url
    author_name
    author_email
    m_counter_id
    /
  )
{
    is(
#       *{ 'WBOX::Model::Widget::'.$_ }($wi35),
        $wi35_2->$_(),
        $wi35->$_(),
#       *{ 'WBOX::Model::Widget::'.$_ }($wi35_2),
        $_
    );
}

SKIP: {
    skip 'not implemented in widb yet', 3;
    for (
        qw/
        alias
        salt
        salt_prev
        /
      )
    {
        is(
            $wi35_2->$_(),
            $wi35->$_(),
            $_
        );
    }

}

#SET TO undef or null
for (
    qw/
    regional_dt catalog_request_dt regreject_reason  stale_rss
    catalog_dt catalog_request_dt catreject_reason
    warning_dt
    warning_reason
    in_catalog
    in_regional
    title_url
    author_name
    author_email
    m_counter_id
    /
  )
{

    is($wi35_2->$_(''), '', 'set undef for ' . $_);

}

ok($wi35_2->actflag('active'));

$WBOX::Requester::requester->widget_update(
    $wi35_2,
    WADM::Utils::get_master_retry_pattern(),
#   WADM::Conf->get('WboxDBMaster'),
    2
);

my $wi35_3 = WADM::Index::widget_by_wid(35);

for (
    qw/regional_dt regflag regreject_reason
    titleurl title
    title_url
    author_email
    author_name
    m_counter_id
    /
  )
{

    is(
        $wi35_3->$_(),
        $wi35_2->$_(),
        'null at ' . $_
    );

}

is($wi35_3->actflag(), 'active', 'Active at end');

