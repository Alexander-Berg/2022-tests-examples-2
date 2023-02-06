package Jobs::test_rss;
use lib::abs qw(..);
## no critic (ValuesAndExpressions::ProhibitMixedBooleanOperators)

use strict;
use warnings;
use starter;

use Jobs::monitoring;
use Jobs::test_no_rss;
use WADM::History;
use WADM::Utils;
use WADM::Conf;
use Time::HiRes qw(sleep);

use utf8;

our $test = {
    saved  => 0,
    mailed => 0,
};

sub run {

    logit('debug', 'Testing renew of rss widgets');
    starter::init_wadm();
    starter::init_wbox();
    #starter::init_wadm_tt();
    starter::init_reasons();
    require WADM::History;
    require WADM::Monitoring;
    require WADM::WidgetMailer;

    starter::require_history();

    Jobs::test_no_rss::test_access();

    main::find_widgets(
        filter => {
#            catflag => 'inside',
            wtype => 'inline',
            # lang  => '%tr%'
        },
        callback => \&process,
        order    => 'users.desc',
        #limit => 400,
    );

    if (!starter::c('lazy') and !$test->{saved}) {
        logit('interr', "Zerro widgets saved - possible error");
        return 0;
    }
    return 1;
}

sub process {
    our $wadm_tt_obj;
    my $force  = $_[1];
    my $widget = shift;

    unless (main::is_popular($widget, 0, 'rss') or $widget->stale_rss()) {
        return 0;
    }

    my $was_rotten = $widget->stale_rss();

    #logit( 'debug' , 'Testing rottenes of widget rss: '.$widget->id() );
    my $status = WADM::Monitoring::test_widget_rss($widget, $force);
    my $ok = $status->{status};
    #my $ok = WADM::Monitoring::test_if_rss_new( $widget, $force );
    unless ($ok) {
        logit('debug', 'found rotten widget:' . ($widget->defaultvalue('url') || ''));
        logit('monitoring', 'RSSOLD Widget ' . $widget->id() . ' will be rejected wia RSS monotoring');
    }

    if ((
            $widget->can_stale_rss()
            and (defined $status->{rss_entries})
            and ($status->{rss_entries} == 0)

        )
        or $widget->no_rss()
        or ($widget->dont_work_complex() and $widget->dont_work_complex()->{td}->{norss})
      ) {
        #add every susspected widget to no-rss monitoring
        #
        logit('debug', " add widget to no-rss monitoring " . $widget->id());
        #print Data::Dumper::Dumper( $widget->can_stale_rss(),  $status,  $widget->no_rss(), $widget->dont_work_complex() );
        Jobs::test_no_rss::add_widget_to_no_rss_monitorig($widget);

        WADM::WatchDog::add_event('no_rss_q', 1) if !$status->{non_rss}
    } else {
        WADM::WatchDog::add_event('no_rss_q', 0) if !$status->{non_rss}
    }

    #my $old_dirty = $widget->dirty_rss();
    #WADM::Monitoring::test_widget_rss_content( $widget, $force );
    #my $dirty = $widget->dirty_rss();

    if (starter::c('lazy')) {
        return 1;
    }

    #my $response = WADM::Auto::dirty_rss( widget => $widget, login => 'autobot', value => $dirty, old_value => $old_dirty);
    my $response = WADM::Auto::rotten_rss(
        widget => $widget,
        login  => 'autobot'
    );

    unless ($widget->is_changed()) {
        return 1;
    }

    #save changes
    #in several cases well not send email;
    unless (ok_db_resp(main::widget_update($widget))) {
        logit('interr', 'Widget save failed, mail not send');
    } else {
        WADM::Auto::mail_and_log($response);
    }
    #Time::HiRes::usleep(200000) unless starter::c('fast');

    $test->{saved}++;
    return 1;
}

1;
