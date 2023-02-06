package MordaX::Block::Taxi_newbie::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Block::Taxi_newbie;

use MP::Logit qw(dmp logit traceit);
use MP::Utils;


sub setup : Test(setup) {
    my $self = shift;

    $self->{req} = MordaX::Req->new();
}

sub test__is_block_enabled : Test(4) {
    my $self = shift;

    no warnings qw(redefine);
    local *_is_block_enabled = \&MordaX::Block::Taxi_newbie::_is_block_enabled;

    my $req = {UID => 1};
    local *MordaX::Type::is_api_search_2_only = sub { 1 };
    local *MordaX::Type::is_required_app_version = sub { 1 };
    local *MordaX::Options::options = sub {
        return 0 if ($_[0] eq 'disable_taxi_newbie');
    };

    is_deeply(_is_block_enabled($req), 1, "all is ok");

    $req = {UID => 1};
    *MordaX::Options::options = sub {
        return 1 if ($_[0] eq 'disable_taxi_newbie');
    };

    is_deeply(_is_block_enabled($req), '', "disable_taxi_newbie is on");

    $req = {UID => 1};
    *MordaX::Type::is_required_app_version = sub { 0 };
    *MordaX::Options::options = sub {
        return 0 if ($_[0] eq 'disable_taxi_newbie');
    };

    is_deeply(_is_block_enabled($req), 0, "is_required_app_version false");

    $req = {UID => 1};
    *MordaX::Type::is_api_search_2_only = sub { 0 };
    *MordaX::Type::is_required_app_version = sub { 1 };

    is_deeply(_is_block_enabled($req), 0, "is_api_search_2_only false");
}

sub test__is_taxi_newbie : Test(4) {
    my $self = shift;

    no warnings qw(redefine);
    local *is_taxi_newbie = \&MordaX::Block::Taxi_newbie::is_taxi_newbie;
    local *MordaX::HTTP::new = sub { $self };
    local *alias_exists = sub { 1 };
    local *result_req_info = sub {
        return {
            success => 1,
            response_content => '{}',
        };
    };
    my $error_type = '';
    local *MordaX::Block::Taxi_newbie::logit = sub {
        $error_type = $_[0];
    };
    is_deeply(is_taxi_newbie({}), undef, "response_content is empty json");
    is($error_type, 'nodata');

    *result_req_info = sub {
        return {
            success => 1,
            response_content => '{"is_new_user": false}',
        };
    };
    is_deeply(is_taxi_newbie({}), '', "valid json and is_new_user is false");

    *result_req_info = sub {
        return {
            success => 1,
            response_content => '{"is_new_user": true}',
        };
    };
    is_deeply(is_taxi_newbie({}), 1, "valid json and is_new_user is false");
}

1;