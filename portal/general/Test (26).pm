package Handler::Widget::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

#use MP::Logit qw(logit dmp);

use Handler::Widget;
use MordaX::Input;


sub test_prepare_geo_args : Test(5) {
    my $self = shift;

    *prepare_geo_args = \&Handler::Widget::_prepare_geo_args;
    *extend_device = \&MordaX::Input::extend_device_for_search_app;

    my @data;
    my $req = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 8040000,
            from         => 'searchapp',
            lat => 1,
            lon => 1,
            location_recency  => 60,
            location_accuracy => 100,
            ll => '2,2',
        },
    };
    my $req_after = {%$req};
    push @data, [$req, $req_after];
    $req = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 8040000,
            from         => 'searchapp',
            lat => 1,
            lon => 1,
            location_recency  => 60 * 60 * 2 * 1000 + 1,
            location_accuracy => 100,
            ll => '2,2',
        },
    };
    $req_after = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 8040000,
            from         => 'searchapp',
            lat => 2,
            lon => 2,
            location_recency  => 600000,
            location_accuracy => 85,
        },
    };
    push @data, [$req, $req_after];
    $req = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 7040000,
            from         => 'searchapp',
            lat => 1,
            lon => 1,
            location_recency  => 60,
            location_accuracy => 100,
            ll => '2,2',
        },
    };
    $req_after = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 7040000,
            from         => 'searchapp',
            lat => 2,
            lon => 2,
            location_recency  => 600000,
            location_accuracy => 85,
        },
    };
    push @data, [$req, $req_after];
    $req = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 6040000,
            lat => 1,
            lon => 1,
            location_recency  => 60,
            location_accuracy => 100,
            ll => '2,2',
        },
    };
    $req_after = {%$req};
    push @data, [$req, $req_after];
    $req = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 6040000,
            lat => 1,
            lon => 1,
            location_recency  => 60 * 60 * 2 * 1000 + 1,
            location_accuracy => 100,
            ll => '2,2',
        },
    };
    $req_after = {
        Getargshash => {
            app_platform => 'android',
            app_version  => 6040000,
            ll => '2,2',
        },
    };
    push @data, [$req, $req_after];

    for (@data) {
        # my ($req, $req_after) = @$_;
        $_->[0]->{UserDevice} = {
            app_platform => $_->[0]->{Getargshash}->{app_platform},
            app_version  => $_->[0]->{Getargshash}->{app_version},
        };
        prepare_geo_args(undef, $_->[0]);
        delete $_->[0]->{cache};
        delete $_->[0]->{UserDevice};
        is_deeply($_->[0], $_->[1]);
    }
}


1;
