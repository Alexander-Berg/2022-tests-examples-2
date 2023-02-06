#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

require WADM::Index;
use WBOX::Model::Widget;
use WBOX::Requester;
use WADM::Utils;

diag('making request');
my $resp_data = $WBOX::Requester::requester->wboxdb_request({
        with_all => 1,
        order    => 'users.dsc',
        limit    => 2,
    },
    'admallwidgets',
    WADM::Utils::get_db_url(),
);
my $data = $resp_data->{data};

foreach (@$data) {
    delete $_->{wdata};
}

print Data::Dumper::Dumper($data);

