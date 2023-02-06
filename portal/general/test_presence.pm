package Jobs::test_presence;

use strict;
use warnings;
use WBOX::Utils;
use WADM::Utils;
use WADM::Conf;

use Time::HiRes;

use utf8;

our $mh;
our $open_widgets = {};

sub run {
    logit('debug', 'Testing presence of widgets');
    unless (WADM::Conf->new()) {
        starter::failed('wadm config not inited ');
    }
    starter::init_wbox();
    require WADM::History;
    require WADM::Monitoring;
    require WADM::WidgetMailer;
    require Template;

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

    require MordaX::HTTP;
    $mh = MordaX::HTTP->new({});

    main::find_widgets(
        filter => {
#            catflag => 'inside',
            'wtype' => 'iframe'
        },
        callback => \&process2,
        limit    => 2000,
    );

    logit('debug', 'Job Finished grabbing request');
    my $cx = 0;
    while ($cx < 1000 and scalar keys %$open_widgets) {
        $cx++;
        sleep 1;
        process_requests();
    }

    logit('debug', 'Job Finished, on ' . $cx);

}

sub process2 {
    my $widget = shift;

    place_request($widget);
    process_requests();
}

=x
we sholud have 2 linked storages
    1. in http object
    2. http object to widget 

    WIDGET 
    -> SRC !
    -> TITLE_URL !

=cut

#loader -> load to array -> load to HTTP getter -> cycle -> scan ->

sub place_request {

    my $widget = shift;

    my $widget_desc = {
        widget => $widget,
        id     => $widget->id(),
    };

    #place requestess
    my $alias = 'w' . $widget->id();
    if ($widget->titleurl()) {

        my $url  = $widget->titleurl();
        my $name = $alias . 't';
        logit('debug', " $name: $url ");

        $mh->add(
            'alias'   => $name,
            'url'     => $url,
            'timeout' => 5,
            'slow'    => 1,
            'retries' => 2,
            'headers' => [
                {'name' => 'User-Agent', 'value' => 'Wbox tester',},
            ],
        );

        $widget_desc->{titleurl} = {
            alias  => $name,
            url    => $url,
            status => undef,
        };
    }
    if ($widget->src()) {
        my $url = $widget->src();
        if ($url =~ m/^\/wy/) {
            $url = 'http://www.yandex.ru' . $url;
        }
        my $name = $alias . 's';
        logit('debug', " $name: $url ");
        $mh->add(
            'alias'   => $name,
            'url'     => $url,
            'timeout' => 5,
            'slow'    => 1,
            'retries' => 2,
            'headers' => [
                {'name' => 'User-Agent', 'value' => 'Wbox tester',},
              ]
        );
        $widget_desc->{src} = {
            alias  => $name,
            url    => $url,
            status => undef,
        };
    }

    unless (all_done($widget_desc)) {
        logit('debug', " Palacing request on: " . $widget->id(),);
        $open_widgets->{$widget_desc->{id}} = $widget_desc;
    }

}

sub process_requests {
    my %attr = @_;
    $mh->poke();
    foreach my $widget_desc (values %$open_widgets) {
        my $widget = $widget_desc->{widget};
        next unless $widget;

        my $alias = 'w' . $widget_desc->{id};

        if ($widget_desc->{src}) {
            extract_status_to($widget_desc->{src});
        }
        if ($widget_desc->{titleurl}) {
            extract_status_to($widget_desc->{titleurl});
        }

        finilize($widget_desc) if all_done($widget_desc);

    }
}

sub extract_status_to {
    my $request_desc = shift;
    return if defined $request_desc->{status};
    my $alias = $request_desc->{alias};
    my $done  = $mh->done($alias);
    if ($done) {
        my $content = $mh->result($alias);
        if ($content) {
            $request_desc->{status} = 'ok';
            logit('debug', " alias: $alias, content: ok");

        } else {
            #getting error
            $request_desc->{status} = 'fail';
        }
    }
}

sub all_done {
    my ($widget_desc) = @_;
    return undef if ($widget_desc->{src} and (not defined $widget_desc->{src}->{status}));
    my $count = scalar grep { $widget_desc->{$_} and (not defined $widget_desc->{$_}->{status}) } (qw/src titleurl/);
    return 1 unless $count;
    return undef;
}

sub finilize {
    my ($widget_desc) = @_;
    use Data::Dumper;
    #print "READY: ". Dumper( $widget_desc->{titleurl},$widget_desc->{src}, );

    my $widget = $widget_desc->{widget};

    if ($widget_desc->{titleurl}) {
        $widget->titleurl_available(($widget_desc->{titleurl}->{status} eq 'ok') ? 1 : 0);
    }
    if ($widget_desc->{src}) {
        $widget->src_available(($widget_desc->{src}->{status} eq 'ok') ? 1 : 0);
    }

    do_the_other_staff($widget);

    delete $open_widgets->{$widget_desc->{id}};
}

sub do_the_other_staff {
    my ($widget) = @_;

    my $branch;
    if ($widget->bad_response()) {
        logit('interr', "Detected SRC BAD widget: " . $widget->id());
        $branch = 'src_fail';
    } else {
        $branch = 'ok';
    }

    my $auto_old = $widget->autostatus();
    my $auto     = main::get_new_autostatus($widget);

    # we ADD warning, to  info user of full PIZDEC
    # and drop it!

    # WARNING
    if ($branch eq 'src_fail') {
        $widget->warning_add('src', ' your widget dont respond!');
        $auto->{warning}->{src} = 1;
    } else {

        if ($auto->{warning}->{src}) {
            $widget->warning_drop('src');
            delete $auto->{warning}->{src};
        }
    }
    # EXCLUDION FROM PRORAMS
    if ($branch eq 'src_fail') {
        if ($auto->{reason} and $auto->{reason}->{src}) {
            #all ready detected
        } else {
            $auto->{reason}->{src} = 1;
        }
    } else {
        if ($auto->{reason}->{src}) {
            delete $auto->{reason}->{src};
        }
    }

    unless (ok_db_resp(main::widget_update($widget))) {
        logit('interr', 'Widget save failed, mail not send');
    }

}

1;
