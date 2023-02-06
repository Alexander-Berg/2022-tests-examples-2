package Handler::Api::Test;

use rules;

use Test::Most;
use base qw(Test::Class);
use URI::Split;
use MordaX::Utils;

use MP::Logit qw(logit dmp);

use Handler::Api;

sub test_add_bell_info : Test(4) {
    my $self = shift;

    *add_bell_info = \&Handler::Api::add_bell_info;

    no warnings qw(redefine experimental::smartmatch);
    local *MordaX::Utils::options = sub {return 0};
    local *MordaX::Type::is_api_search_2_only = sub {return 1};
    local *MordaX::Type::is_api_search_only = sub {return 1};
    local *MordaX::Utils::Api::menu_custom_lang = sub {return 1};

    local *lang = sub {return 1};

    local *MordaX::Type::is_required_app_version = sub {return 1};

    my $url_base = 'https://yandex.ru/gnc/frame';
    my $output = {};
    add_bell_info({UID => 'something'}, $output);
    my ($scheme, $host, $path, $query) = URI::Split::uri_split($output->{bell_info}{url});
    is(URI::Split::uri_join($scheme, $host, $path), $url_base, 'check url base searchapp');
    is_deeply(MordaX::Utils::parse_query($query), {'utm_source_service' => 'searchapp'}, 'check query searchapp');

    local *MordaX::Type::is_required_app_version = sub {return 0};
    local *MordaX::Type::is_api_yabrowser_2 = sub {return 1};
    local *MordaX::Type::is_required_app_version = sub {return 1};

    $output = {};
    add_bell_info({UID => 'something'}, $output);
    ($scheme, $host, $path, $query) = URI::Split::uri_split($output->{bell_info}{url});
    is(URI::Split::uri_join($scheme, $host, $path), $url_base, 'check url base browser');
    is_deeply(MordaX::Utils::parse_query($query), {'utm_source_service' => 'browser'}, 'check query browser');

}


sub test_move_values_to_end :  Test(4) {
    my $self = shift;

    *move_values_to_end = \&Handler::Api::move_values_to_end;

    my $list = ['one', 'two', 'three', 'four'];
    my $values_to_move = ['one', 'three'];
    my $results = ['two', 'four', 'one', 'three'];
    is_deeply(move_values_to_end($list, $values_to_move), $results);

    $list = ['one', 'two', 'three', 'four'];
    $values_to_move = ['one'];
    $results = ['two', 'three', 'four', 'one'];
    is_deeply(move_values_to_end($list, $values_to_move), $results);

    $list = [];
    $values_to_move = ['one', 'three'];
    $results = [];
    is_deeply(move_values_to_end($list, $values_to_move), $results);

    $list = ['one', 'two', 'three', 'four'];
    $values_to_move = [];
    $results = ['one', 'two', 'three', 'four'];
    is_deeply(move_values_to_end($list, $values_to_move), $results);
}

1;
