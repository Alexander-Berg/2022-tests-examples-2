package MordaX::Banner::Direct::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Banner::Direct;

use MP::Logit;

sub setup : Test(setup) {
    my $self = shift;

    my $req = MordaX::Req->new();
    $self->{direct} = MordaX::Banner::Direct->new($req);
    $self->{req} = $req;

    no warnings 'redefine';
    *MordaX::Data_get::get_static_data = sub {
        return {page_backfill => 123, page_firstlook => 456, exp => 'exp'};
    };

    *MordaX::Experiment::AB::flags = sub($) {
        return $self;
    };

    *MordaX::Banner::Direct::logit = sub {
        $self->{error_text} = [@_];
    };
}

sub test_get_refresh_params : Test(2) {
    my $self = shift;

    no warnings qw(redefine experimental::smartmatch);

    *get_refresh_params = \&MordaX::Banner::Direct::get_refresh_params;
    local *MordaX::Banner::Direct::get_data_banners_refresh = sub {
        return {
            content => 'all',
            domain => 'ru',
            geos => 225,
            meta_refresh => 100000,
            impid => 1,
        }
    };
    is_deeply(get_refresh_params($self->{direct}, $self->{req}), {
        refresh_counts => 10,
        watch_timeout => 90,
        tab_timeout => 10,
        overlapping_timeout => 10,
        refresh_url => '/portal/ntp/banner',
    }, 'check default params');

    *MordaX::Banner::Direct::get_data_banners_refresh = sub {
        return {
            content => 'all',
            domain => 'ru',
            geos => 225,
            meta_refresh => 100000,
            impid => 1,
            refresh_counts => 11,
            watch_timeout => 99,
            tab_timeout => 13,
            overlapping_timeout => 15,
            refresh_url => '/portal/ntp/banner/test'
        }
    };
    is_deeply(get_refresh_params($self->{direct}, $self->{req}), {
        refresh_counts => 11,
        watch_timeout => 99,
        tab_timeout => 13,
        overlapping_timeout => 15,
        refresh_url => '/portal/ntp/banner/test',
    }, 'check with custom params');
}

sub test_get_page : Test(2) {
    my $self = shift;

    no warnings 'redefine';
    *get_page = \&MordaX::Banner::Direct::get_page;

    local *MordaX::Type::is_banner_refresh = sub {
        return $_[0]->{is_banner_refresh};
    };

    my $req = {
        is_banner_refresh => 1,
    };

    $self->{alias_for_test} = 'page_backfill';
    is(get_page($self, $req), 1234);

    $self->{page} = undef;
    $req->{is_banner_refresh} = 0;
    $self->{alias_for_test} = 'page_backfill';
    is(get_page($self, $req), 111);
}

sub test_get_madm_impid : Test(2) {
    my $self = shift;

    no warnings 'redefine';
    *get_madm_impid = \&MordaX::Banner::Direct::get_madm_impid;

    local *MordaX::Type::is_banner_refresh = sub {
        return $_[0]->{is_banner_refresh};
    };

    *MordaX::Banner::Direct::get_data_banners_refresh = \&get_data_banners_refresh;
    *MordaX::Banner::Direct::get_data_direct_geo = \&get_data_direct_geo;

    my $req = {
        is_banner_refresh => 1,
    };

    $self->{imp_alias_for_test} = 'impid_backfill';
    is(get_madm_impid($self, $req), 1);

    $self->{page} = undef;
    $req->{is_banner_refresh} = 0;
    $self->{imp_alias_for_test} = 'impid_backfill';
    is(get_madm_impid($self, $req), 10);
}

sub get_data_banners_refresh {
    my $req = shift;

    return {
        content => 'all',
        domain => 'ru',
        geos => 225,
        meta_refresh => 1234,
        impid => 1,
        refresh_counts => 11,
        watch_timeout => 99,
        tab_timeout => 13,
        overlapping_timeout => 15,
        refresh_url => '/portal/ntp/banner/test'
    };
}

sub get_data_direct_geo {
    my $req = shift;

    return {
        content => 'all',
        domain => 'ru',
        geos => 225,
        page_backfill => 111,
        impid_backfill => 10,
        page_firstlook => 222,
        impid_firstlook => 2,
        page_rtbmeta => 333,
        impid_rtbmeta => 3,
        page_refresh_backfill => 444,
        page_refresh_firstlook => 555,
    };
}

sub page_alias {
    my $self = shift;

    return $self->{alias_for_test};
}

sub impid_alias {
    my $self = shift;

    return $self->{imp_alias_for_test};
}

1;
