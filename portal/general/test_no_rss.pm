package Jobs::test_no_rss;
use lib::abs qw(..);

use strict;
use warnings;
use starter;
## no critic (BuiltinFunctions::ProhibitUniversalCan)
## no critic (BuiltinFunctions::ProhibitUniversalIsa)
## no critic (ValuesAndExpressions::ProhibitMixedBooleanOperators)

use Jobs::monitoring;
use WADM::History;
use WADM::Utils;
use WADM::Auto;
use WADM::Index;
use Time::HiRes qw(sleep);
use File::Spec;
use Storable;

use Data::Dumper;

use utf8;

our $test = {
    saved  => 0,
    mailed => 0,
};

our $state = {widget_blocks => []};

sub init {
    starter::init_wadm();
    starter::init_wbox();
    #starter::init_wadm_tt();
    starter::init_reasons();

    starter::require_history();
    require WADM::History;
    require WADM::Monitoring;
    require WADM::WidgetMailer;
}

sub run {
    init();

    logit('debug', 'Testing no-rss of widgets');

    test_access();

    load_state();
    add_new_widgets();

    #!/ load scanned widgets
    my $list = $state->{widget_blocks};
    foreach my $block (@$list) {
        eval { process($block); };
        logit('interr', $@) if $@;
    }

    store_state();

#    if ( !starter::c( 'lazy' ) and !$test->{saved} ){
#        logit('interr', "Zerro widgets saved - possible error" );
#        return 0;
#    }
}

sub state {
    init();
    load_state();

    foreach my $b (@{$state->{widget_blocks}}) {

        my $wid = $b->{wid};
        my $state = ($b->{last_offline} > $b->{last_online}) ? 'offline' : ' online';

        my $offline = $b->{last_offline} - $b->{first_offline};
        my $online  = $b->{last_online} - $b->{first_online};
        printf(' Widget: %5d now %s, last online for %5d sec, last offline %5d for sec', $wid, $state, $online, $offline);
        print "\n";
    }
    return 1;
}

sub process {
    my $data = shift;
    #watch data
    # wid
    # histort
    #   [ time, status ]
    # last online
    # first online
    # last offline
    # first offline

    #dump_block( $data );

    my $wid = $data->{wid};
    #logit( 'debug', "Processing block ". $wid );

    my $widget = main::widget_by_wid($wid);
    unless ($widget) {
        logit('debug', "failed to load widget $wid");
        #db fail? or no widget
        forget($wid);
        return 1;
    }
    unless ($widget->can_stale_rss()) {
        logit('debug', "widget $wid is not designed for rss");
        my $auto_response = WADM::Auto::no_rss(widget => $widget, login => 'autobot');
        if ($auto_response) {
            #save
            #send
            save_and_notify($widget, $auto_response);
        }

        if ($widget->no_rss()) {
            #remove from monitoring
        }

        #db fail? or no widget
        forget($wid);
        return 1;

    }
    my $was_no_rss = $widget->no_rss() || 0;
    my $status = WADM::Monitoring::test_widget_rss($widget);
    #logit( 'debug', " Monitorign results: ". Data::Dumper->Dump( [ $status ] , [qw/status/] ) );

    my $auto_response;

    push @{$data->{history}}, {'time' => time, status => $status};
    #limit input
    $data->{history} = [grep { time() - $_->{'time'} < 48 * 3600 } @{$data->{history}}];

    if (defined $status->{rss_entries}) {
        #undef on errors
        if ($status->{rss_entries}) {
            # online
            logit('debug', "widget $wid online now");
            $widget->no_rss(0);
            $data->{last_online} = time();
        } else {
            $data->{last_offline} = time();
            my $off_hours = sprintf("%.1f", ($data->{last_offline} - $data->{first_offline}) / 3600);
            my $notified = ($widget->autostatus() and $widget->autostatus()->{dontwork}->{norss}) ? " notification send " : '';
            logit('debug', "widget $wid offline now $off_hours hours $notified ");
            $widget->no_rss(1);
        }
    }

    if (!$was_no_rss and $status->{rss_entries} = 0) {
        $data->{first_offline} = time();
    } elsif ($was_no_rss and $status->{rss_entries}) {
        $data->{first_online} = time();
    }

    #fistt off line more than 12 hours and

    $auto_response = WADM::Auto::no_rss(widget => $widget, login => 'autobot');

    save_and_notify($widget, $auto_response);

    # forget it to long too bad
    if ($widget->no_rss() and ((time - ($data->{first_offline} || time)) > 24 * 3600)) {
        forget($wid);
    }

    # forget it, it is still cool
    if (!$widget->no_rss() and ((time - ($data->{first_online} || time)) > 24 * 3600)) {
        forget($wid);
    }

    #save and email, if needed
    return $data;
}

sub save_and_notify {
    my ($widget, $response) = @_;
    unless (ok_db_resp(main::widget_update($widget))) {
        logit('interr', 'Widget save failed, mail not send');
    } else {
        WADM::Auto::mail_and_log($response);
    }
    return 1;
}

sub add_new_widgets {
    my $newfile = File::Spec->catfile('/var/exports', 'no_rss.new');
    unless (open(IN, $newfile)) {
        return;
    }
    while (<IN>) {
        if (m/(\d+)/) {
            add_block_for($1);
        }
    }
    close(IN);
    open(IN, ">$newfile");
    close(IN);
}

sub add_block_for {
    my $wid = shift;
    unless (get_block($wid)) {
        my $block = {
            wid           => $wid,
            history       => [],
            last_offline  => time,
            last_online   => time,
            first_offline => time,
            first_online  => time,
        };
        logit('debug', "add widget $wid  for monitoring");
        unshift(@{$state->{widget_blocks}}, $block);
    }
}

sub get_block {
    my $wid    = shift;
    my $blocks = $state->{widget_blocks};
    for (my $i = 0; $i < @$blocks; $i++) {
        my $block = $blocks->[$i];
        if ($block->{wid} == $wid) {
            return ($block, $i) if wantarray;
            return $block;
        }
    }
    return undef;
}

sub forget {
    my $wid = shift;
    my ($block, $index) = get_block($wid);
    if ($block) {
        logit('debug', "remove widget $wid from monitoring");
        #logit('debug', "history " . Data::Dumper::Dumper($block));
        my $blocks = $state->{widget_blocks};
        delete $blocks->[$index];
        $state->{widget_blocks} = [grep {$_} @$blocks];

        #dump hisptry
    }
}

sub dump_block {
    my $block = shift;
    unless (ref($block)) {
        $block = get_block($block);
    }
    print Data::Dumper->Dump([$block], [qw/block/]);
}

sub load_state {
    my $statefile = File::Spec->catfile('/var/exports', 'no_rss.state');
    my $currentstate;
    eval { $currentstate = retrieve($statefile); };
    if ($@) {
        my $msg = $@;
        $msg =~ s/[\n\r]+/ /mog;
        $msg =~ s/at\s[^\s]+line\s\d+$//og;
        logit('error', "Failed to retrieve current state: $msg", 3);
    }

    if (UNIVERSAL::isa($currentstate, 'HASH') && defined($currentstate->{'widget_blocks'})) {
        $state = $currentstate;
    }
    return $currentstate;
}

sub store_state {
    my $statefile = File::Spec->catfile('/var/exports', 'no_rss.state');
    eval { store($state, $statefile); };
    if ($@) {
        my $msg = $@;
        $msg =~ s/[\n\r]+/ /mog;
        $msg =~ s/at\s[^\s]+line\s\d+$//og;
        logit('error', "Failed to store current state: $msg");
        exit(7);
    } else {
        logit('debug', 'stored ok');
    }
}
#external functions
sub test_access {
    my $newfile = File::Spec->catfile('/var/exports', 'no_rss.new');
    unless (open(IN, ">>" . $newfile)) {
        logit('interr', "Write to $newfile failed  - check rights");
        return 0;
    }
    close(IN);
    return 1;

}

sub add_widget_to_no_rss_monitorig {
    my $widget = shift;
    return undef unless $widget;
    my $wid = $widget->id();
    my $newfile = File::Spec->catfile('/var/exports', 'no_rss.new');
    chmod 0666, $newfile;
    unless (open(IN, ">>" . $newfile)) {
        logit('interr', "Write to $newfile failed check rights");
        return undef;
    }
    print IN $wid . "\n";
    close(IN);
    return 1;
}

