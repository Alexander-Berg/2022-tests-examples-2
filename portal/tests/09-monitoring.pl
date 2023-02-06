#!/usr/bin/perl

use Test::More qw(no_plan);

use lib::abs qw(. ../scripts/);

use common;
use strict;
use warnings;

use POSIX;
#--------------------------
#we  just testing mail mode
#----------

use WADM::WidgetMailer;
#WADM::Mailer;

#load widget
#
require WADM::Index;
use WBOX::Model::Widget;
use WADM::Monitoring;
use WADM::History;
use WADM::Conf;

eval {
    *CORE::GLOBAL::exit = sub {
        die 'exit from eval';
    };
    $ARGV[0] = '--base=' . lib::abs::path('../..');
    my $pl_file = lib::abs::path('../scripts/widgets_job.pl');
    require $pl_file;
};

#like( $@, qr{exit from eval}, 'requred with out errors' );
is($@, '', 'requred with out errors');

require Jobs::test_rss;
require Jobs::test_presence;

starter::init_wadm();
#starter::init_wadm_tt();
#ok($main::wadm_tt_obj, 'WADM TT inited');
starter::init_wadm();

starter::init_wbox();
starter::init_reasons();

ok(starter::c {'widb_master'}, 'url master ok');
ok(starter::c {'widb_replic'}, 'replica');

my $w_photo = WADM::Index::widget_by_wid(22795);
ok($w_photo);
is($w_photo->type,   'inline');
is($w_photo->born(), 'photo');
ok(WADM::Monitoring::test_if_rss_new($w_photo, 'force'), 'rss is new');

my $wi_new = WBOX::Model::Widget->new();
is($wi_new->stale_rss_after(), 4, 'Default after stale ok');

#Only if test failed
$WBOX::Requester::requester->{debug} = 0;

my $wi36 = WADM::Index::widget_by_wid(36);
ok($wi36, 'widget 36 found');
is($wi36->id(), 36, 'id ok');

is($wi36->stale_rss_after(), 5, 'Stale after 5 weeks');
ok($wi36->defaultvalue('url'),     'widget Rss URL defined ');
ok($wi36->defaultvalue('feed_id'), 'widget Rss feed_id defined ');

#is( $wi36->rss_status() , 'ok'        , 'PBB Status ok' );
ok($wi36->rss_last_tested_ts(), 'old testes ts found');
#ok( $wi36->titleurl_available_ts(), 'old title test ts found' );

ok(WADM::Monitoring::test_if_rss_new($wi36, 'force'), 'rss is new');
my $tested = $wi36->rss_last_tested_ts();
ok($wi36->rss_last_tested_ts(),              'old testes ts found');
ok(WADM::Monitoring::test_if_rss_new($wi36), 'rss is new');
is(
    $wi36->rss_last_tested_ts(), $tested
    , 'old testes ts found'
);
is(
    $wi36->get()->{__RSS_LAST_TESTED_TS}, $tested
    , 'export of last test date'
);

ok($wi36->stale_rss_after(5));
is($wi36->stale_rss_after(), 5);
ok(!$wi36->src_failed_ts(''));
ok(!$wi36->rss_last_ts(''));

is($wi36->rss_last_ts, '');
#is( scalar( $wi36->ts_for_user_delete() )  , 2);
ok($wi36->rss_last_ts(time - ($wi36->stale_rss_after() * 3600 * 24 * 7) - 3000));
like(ts_to_date($wi36->rss_last_ts), qr{\d{4}-\d{2}-\d{2} \d});
ok($wi36->suggest_delete(), 'Yp will delete it soon');
is($wi36->force_delete(), 0, 'but not now');
ok($wi36->src_failed_ts(time - 26 * 3600));
#ok( $wi36->force_delete() , 'force delete by RSS');
$tested = $wi36->rss_last_tested_ts();
$wi36->{__UPDATED} = 1;

my $upd = {
    wid     => $wi36->id(),
    wdata   => $wi36->get(),
    updated => 1,
};
#ok( $wi36->titleurl_available_ts(), 'new title test ts found' );
ok(WBOX::Utils::ok_db_resp(widget_update($wi36)), 'update');

my $wi36_2 = get(36);

ok($wi36_2, 'widget 36 found');
is(
    $wi36_2->rss_last_tested_ts(), $tested
    , 'saveed tested ts found'
);
ok($wi36_2->updated(), 'epp updated');

$upd = {
    wid => $wi36->id(),
#   wdata   => $wi36->get(),
    updated => 0,
};
ok(
    WBOX::Utils::ok_db_resp(
        wboxdb_request(
            $upd,
            'updwidget',
            'master'
          )
    ),
    'updated roll back'
);

is(
    WADM::Index::widget_by_wid(36)->updated(), 0,
    , 'updated flag dropped'
);
#---------------
my $tu_ts = $wi36->titleurl_available_ts();
WADM::Monitoring::test_if_titleurl_available($wi36, 'force');
#ok( Jobs::test_presence::process($wi36), 'widget presence ok' );
ok($wi36->titleurl_available,    'TUTL available');
ok($wi36->titleurl_available_ts, 'TS ok');
#my $tu_ts = $wi36->titleurl_available_ts();

my $wi36_3 = WADM::Index::widget_by_wid(36);
is(
    $wi36_3->titleurl_available_ts(), $tu_ts
    , 'ts of TU saved ok'
);

#---------------------------------------------
# now cracking widget to test exclusion
#
my $test_widget_id = 4158;
my $w              = get($test_widget_id);
#-----------------------------------------
$w->autostatus({});
$w->no_rss(0);
$w->yandex(0);
#-----------------------------------------
save($w);
$w = get($test_widget_id);

ok($w, ' W Loaded');
$w->{__USERS} = 300;
$w->{__BORN}  = 'rss';
ok($w->users(), ' 300 users');

#ok( WADM::Utils::test_widget_programs_consistence( $w ) , 'porograms consistance');
my $exclude_res = WADM::Utils::exclude_widget_from_programs($w, q{test}, 'test');
#is( WADM::Utils::exclude_widget_from_programs( $w, q{test}, 'test' )->{count}, 0, 'no in programs' );

ok(WADM::Utils::test_widget_programs_consistence($w), 'porograms consistance');

my %cat_data = (
    'wid'   => $w->id(),
    'uid'   => $w->uid(),
    'wtype' => $w->type(),
    'title' => $w->title(),
    'wdata' => $w->get(),
);
wboxdb_request(\%cat_data, 'addcatalogwidget', 'master');
$w->catflag('inside');

ok(WADM::Utils::test_widget_programs_consistence($w), 'porograms consistance');

my $exclude = WADM::Utils::exclude_widget_from_programs($w, q{test2}, 'test');
is($exclude->{count}, 1);
ok($exclude->{catalog}, 'excluded from catalog');

my $save_monitorin_ref = \&WADM::Monitoring::test_if_rss_new;
#WADM::Monitoring::test_if_rss_new
*WADM::Monitoring::test_widget_rss = sub {
    #   warn 'YEPP, we integrated into monotoring';
    my $w = shift;
    $w->rss_last_ts(time() - 3600 * 24 * 28 - 300);
    $w->rss_last_tested_ts(time());
    $w->defaultvalue('url', 'http://mellior.ru/rss/rss.xml');
    $w->stale_rss(1);
    return {
        status      => 0,
        rss_entries => 1,
        info        => 'mock',
    };
};
my $mail_sub     = \&WADM::WidgetMailer::mailit;
my $mail_counter = 0;
*WADM::WidgetMailer::mailit = sub {
    $mail_counter++;
    &$mail_sub(@_);
};
our $wadm_tt_obj = Template->new({
        ENCODING     => 'utf8',
        PRE_CHOMP    => 0,
        POST_CHOMP   => 0,
        TRIM         => 0,
        ANYCASE      => 0,
        INCLUDE_PATH => WADM::Conf->get('Templates'),
        ABSOLUTE     => 0,
        RELATIVE     => 1,
        RECURSION    => 1,
        CACHE_SIZE   => undef,                                # undef in this context means "cache all templates"
#        COMPILE_EXT => '.compiled',
#        COMPILE_DIR => $tmpl_cache,
    }
);
ok($wadm_tt_obj, 'tt inited');

wboxdb_request(\%cat_data, 'addcatalogwidget',  'master');
wboxdb_request(\%cat_data, 'addregionalwidget', 'master');
$w->catflag('inside');
$w->regflag('inside');
$w->stale_rss(0);

ok(WADM::Utils::test_widget_programs_consistence($w), 'porograms consistance');

$exclude = WADM::Utils::exclude_widget_from_programs($w, q{test3}, 'test');
is($exclude->{count}, 2, 'Exclude widget from BOTH programs');
ok($exclude->{catalog});
ok($exclude->{regional});

ok(WADM::Utils::test_widget_programs_consistence($w), 'porograms consistance');

wboxdb_request(\%cat_data, 'addcatalogwidget',  'master');
wboxdb_request(\%cat_data, 'addregionalwidget', 'master');
$w->catflag('inside');
$w->catflag('canrequest');
$w->regflag('inside');

ok(WADM::Utils::test_widget_programs_consistence($w), 'porograms consistance');

$w->{changed} = 0;
is($mail_counter, 0);
ok(is_popular($w), 'popular');
is($w->stale_rss_after(), 4,     'standart stale');
is($w->born(),            'rss', 'rss born');
is($w->can_stale_rss($w), 1,     'can stale');

ok(Jobs::test_rss::process($w), 'runing test action over mock object');
is(WADM::Auto::get_rotten_rss_branch($w), 'stale', 'Rss process Stale Branch');
ok($w->stale_rss(), 'rottenes confirmed');
is($mail_counter, 1, 'mail send');
$mail_counter = 1;

ok($w->autostatus()->{excluded_from}->{catalog},  'excluded from catalog saved');
ok($w->autostatus()->{excluded_from}->{regional}, 'excluded from regional saved');

wboxdb_request(\%cat_data, 'addcatalogwidget', 'master');
$w->catflag('inside');
$w->{changed} = 0;

ok(WADM::Utils::test_widget_programs_consistence($w), 'porograms consistance');

ok(Jobs::test_rss::process($w), 'runing test action ( catalog ) over mock object');
is($mail_counter, 2, 'mail');
$mail_counter = 2;
ok(Jobs::test_rss::process($w), 'runing test action ( catalog ) over mock object');
is($mail_counter, 2);
ok(Jobs::test_rss::process($w), 'runing test action ( catalog ) over mock object');
is($mail_counter, 2);
ok(Jobs::test_rss::process($w), 'runing test action ( catalog ) over mock object');
is($mail_counter, 2);

wboxdb_request(\%cat_data, 'addregionalwidget', 'master');
$w->regflag('inside');
$w->{changed} = 0;

ok(WADM::Utils::test_widget_programs_consistence($w), 'porograms consistance');

ok(Jobs::test_rss::process($w), 'RSS fail -> exclude from regional');
$w->{changed} = 0;
is($mail_counter, 3, 'mail');
$mail_counter = 3;
ok($w->autostatus()->{excluded_from}->{regional}, 'excluded from regional saved');
ok($w->autostatus()->{excluded_from}->{catalog},  'excluded from catalog saved');

#print Dumper( $w->autostatus() );

#set flag dont work

subtest "set DONT WORK" => sub {
    plan tests => 7;
    $mail_counter = 3;
    $w->dont_work_recalculate({});
    *WADM::Monitoring::test_widget_rss = sub {
        #   warn 'YEPP, we integrated into monotoring';
        my $w = shift;
        $w->rss_last_ts(time() - 3600 * 24 * 70);
        $w->rss_last_tested_ts(time());
        $w->defaultvalue('url', 'http://mellior.ru/rss/rss.xml');
        $w->stale_rss(1);
        return {
            status      => 0,
            rss_entries => 1,
            info        => 'mock',
        };
    };
    is($mail_counter, 3);
    is($w->dont_work(), 0, 'widget works');
    #is( $w->dont_work_complex(), '', ' no dont work rss reason');

    diag("prepare finished");
    ok(Jobs::test_rss::process($w), 'Warning widget, set dont work');
    ok($w->dont_work_complex());
    ok($w->dont_work_complex()->{text}->{rssold}, ' dont work rss reason');
    is($w->dont_work(), 1, 'widget dont works');
    is($mail_counter,   4, 'mail send!');

    $mail_counter = 3;
};

#not enfought popularyty for CATALOG programm
is($w->users(), 300, 'users 300');
ok(is_popular($w), 'popular');
ok(Jobs::test_rss::process($w, 'force'), 'runing test action ( null ) over mock object');
is($mail_counter, 3);

#switch to RSS OK
#testing recovery
subtest "can be added to catalog with 10 user " => sub {
    plan tests => 5;
    $w->{__USERS} = 10;
    is($w->users(),                   10, '10 users');
    is($w->in_catalog(),              0,  'not incatalg');
    is($w->yandex(),                  0,  'not yandex');
    is($w->catflag(),                 'outside');
    is($w->can_be_added_to_catalog(), 0,  'can NOT be added to catalog');
};
#s( $w->in_regional() )

#has warnings or smth else
#is( $w->can_be_added_to_catalog('ignore'), 1, 'can NOT be added to catalog (despite of users)');

subtest 'recovery w 300 users' => sub {
    plan tests => 26;

    $w->moderated(1);
    $w->{__USERS} = 300;

    *WADM::Monitoring::test_widget_rss = sub {
        #   warn 'YEPP, we integrated into monotoring';

        my $w = shift;
        $w->rss_last_ts(time());
        $w->rss_last_tested_ts(time());
        $w->defaultvalue('url', 'http://mellior.ru/rss/rss.xml');
        $w->calc_stale_rss();
        logit('debug', 'mock call of WADM::Monitoring::test_widget_rss for ' . $w->id());
        return {
            status => $w->stale_rss() ? 0 : 1,
            rss_entries => 1,
            info        => 'mock',
        };
    };
    is($w->users(), 300, 'users 300');

    ok($w->autostatus()->{excluded_from}->{regional}, 'will be recover to regional');
    ok($w->autostatus()->{excluded_from}->{catalog},  'will be recover to catalog');

    is($w->catflag(), q{outside}, 'cat flag outside');
    is($w->regflag(), q{outside}, 'reg flag outside');

    is($w->dont_work(), 1, 'widget dont work ');

    $mail_counter = 3;
    ok($w->stale_rss(), 'widget staled');
    is(WADM::Auto::get_rotten_rss_branch($w), 'stale', 'Branch was stale');

    ok(Jobs::test_rss::process($w, 'force'), 'Recovering widget, mail send');

    is(WADM::Auto::get_rotten_rss_branch($w), 'ok', 'Branch is OK');
    is($w->stale_rss(),                       0,    'widget was staled');
    is($w->no_rss(),                          0,    'no rss - ok');

    ok(WADM::Auto::is_widget_rss_ok($w), 'rss ok');

    is($mail_counter, 4);
    $mail_counter = 4;
    ok(Jobs::test_rss::process($w, 'force'), 'Recovering 2, widget must be ok');
    is($mail_counter, 4);
    ok(Jobs::test_rss::process($w, 'force'), 'Recovering 3, widget must be ok');
    is($mail_counter, 4);
    ok(Jobs::test_rss::process($w, 'force'), 'Recovering 4, widget must be ok');
    is($mail_counter, 4);
    $mail_counter = 3;

    is($w->autostatus()->{excluded_from}->{regional}, undef, 'excluded from regional dropped');
    is($w->autostatus()->{excluded_from}->{catalog},  undef, 'excluded from catalog  dropped');

    is($w->catflag(), q{outside}, 'cat flag setted');
    #is( $w->regflag(), q{inside}, 'reg flag setted' );
    is($w->regflag(), q{inside}, 'reg flag setted');

    is($w->can_be_added_to_regional(), 1, 'can be added to regional');
    is($w->can_be_added_to_catalog(),  0, 'cannot be added to catalog');
};

$w->{__USERS} = 10;
is($w->users(), 10, '10 users');

is($w->can_be_added_to_catalog('ignore'), 0, 'can NOT be added to catalog (despite of users)');

$w->{__USERS} = 600;
is($w->users(),                   600, '600 users');
is($w->can_be_added_to_catalog(), 1,   'can be added to catalog');

subtest 'recovery w 600 users' => sub {
    plan tests => 8;
    $w->autostatus()->{excluded_from}->{catalog} = 1;
    $w->autostatus()->{reason}->{rssold}         = 1;
    ok($w->autostatus()->{excluded_from}->{catalog}, 'will be recover to catalog');

    is($w->catflag(), q{outside}, 'cat flag setted');

    $mail_counter = 3;
    ok(Jobs::test_rss::process($w, 'force'), 'Recovering widget, mail send');
    is($mail_counter, 4,);
    $mail_counter = 3;

    is($w->autostatus->{excluded_from}->{regional}, undef, 'excluded from regional dropped');
    is($w->autostatus->{excluded_from}->{catalog},  undef, 'excluded from catalog  dropped');

    is($w->catflag(), q{inside}, 'cat flag setted');
    is($w->regflag(), q{inside}, 'reg flag setted');
};

#other case
subtest 'recovery w 10 users without regional' => sub {
    plan tests => 7;
    $w->autostatus()->{excluded_from}->{catalog} = 1;
    $w->autostatus()->{reason}->{rssold}         = 1;

    WADM::Utils::exclude_widget_from_programs(
        $w,
        'we need this',
        'autotest',
    );
    $w->autostatus()->{excluded_from}->{regional} = undef;

    ok($w->autostatus()->{excluded_from}->{catalog}, 'will be recover to catalog');
    $mail_counter = 3;
    ok(Jobs::test_rss::process($w, 'force'), 'Recovering widget, mail send');
    is($mail_counter, 4,);
    $mail_counter = 3;
    is($w->autostatus->{excluded_from}->{regional}, undef,      'excluded from regional dropped');
    is($w->autostatus->{excluded_from}->{catalog},  undef,      'excluded from catalog  dropped');
    is($w->catflag(),                               q{inside},  'cat flag setted');
    is($w->regflag(),                               q{outside}, 'reg flag dropped');
};
#testing warning

#switch to rss born
$w->born('rss');
is($w->born(), 'rss');
ok($w->can_stale_rss(), 'can stale rss');

*WADM::Monitoring::test_widget_rss = sub {
#   warn 'YEPP, we integrated into monotoring';
    my $w = shift;
    $w->rss_last_ts(time() - 3600 * 24 * 15);
    $w->rss_last_tested_ts(time());
    $w->defaultvalue('url', 'http://mellior.ru/rss/rss.xml');
    $w->stale_rss(0);
    return {
        status      => 1,
        rss_entries => 1,
        info        => 'mock',
    };
};
#

ok(Jobs::test_rss::process($w), 'Warning widget, mail send');

is($mail_counter, 4);
is($w->autostatus()->{warning}->{rssold}, 1, 'warned for RSS presensents');
ok(Jobs::test_rss::process($w), 'Warning widget, not mail send');
is($mail_counter, 4);
is($w->autostatus()->{warning}->{rssold}, 1, 'warned for RSS presents');
ok(Jobs::test_rss::process($w), 'Warning widget, not mail send');
is($mail_counter, 4);

$mail_counter = 3;

is($mail_counter, 3, 'mail send');

#27548;#
my $w_as770 = WADM::Index::widget_by_wid(27551);
Jobs::test_rss::process($w_as770);

#testing availability
my $save_test_url = \&WADM::Moniring::is_url_available;
*WADM::Monitoring::is_url_available = sub { return 0 };
*WADM::Monitoring::get_url          = sub { return undef };

wboxdb_request(\%cat_data, 'addcatalogwidget',  'master');
wboxdb_request(\%cat_data, 'addregionalwidget', 'master');
$w->catflag('canrequest');
$w->regflag('inside');
$w->{changed} = 0;

subtest "IS_POPULAR" => sub {
    plan tests => 8;
    $w->{__USERS}      = 10;
    $w->{__AUTOSTATUS} = {};
    $w->catflag("outside");
    $w->regflag("outside");

    is(is_popular($w), 0);
    is(is_popular($w, 'force'), 1, 'force works');
    my $auto = $w->autostatus();
    ok($auto, "auto stauts ok");
    is(scalar keys %$auto, 0, "auto sttus empty");
    $auto->{dontwork}->{src404} = 1;
    is(is_popular($w), 1, 'popular by auto status');
    is(is_popular($w, undef, 'xxx'), 0, 'not popular by auto status with unknown type');
    is(is_popular($w, undef, 'rss'), 0, 'not popular by auto status with type rss');
    $auto->{dontwork}->{rssold} = 1;
    is(is_popular($w, undef, 'rss'), 1, 'not popular by auto status with type rss');

};

is($w->no_rss(), 0, 'no rss dropped');

ok(MordaX::Data_get_simple::getblockalldata('domains'), 'domains export loaded');

=old version
ok( Jobs::test_presence::process( $w, 'force' ), 'widget presence fail test' );
ok( $w->is_changed(), 'w changed' );
is( $mail_counter, 4 );

ok( Jobs::test_presence::process( $w, 'force' ), 'widget presence fail test 2' );
is( $mail_counter, 4 );
ok( Jobs::test_presence::process( $w, 'force' ), 'widget presence fail test 3' );
is( $mail_counter, 4 );
ok( Jobs::test_presence::process( $w, 'force' ), 'widget presence fail test 4' );
is( $mail_counter, 4 );
=new

my $wid_hash = { wid => $w->id() };
ok( wboxdb_request( $wid_hash, 'delfromcatalog',  'master' ), 'delete from catalog' );
ok( wboxdb_request( $wid_hash, 'delfromregional', 'master' ), 'delete from regional' );

