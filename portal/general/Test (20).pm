package Handler::Api::UFeed::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MP::Logit qw(logit dmp);

use Handler::Api::UFeed;

sub test_get_feed1_instance : Test(1) {
    my $self = shift;

    *test_func = \&Handler::Api::UFeed::instance;

    no warnings qw(redefine experimental::smartmatch);
    local *MordaX::Utils::options = sub { return 0; };
    local *MordaX::Type::is_api_search_2_strict = sub { return 1; };
    local *MordaX::Type::is_app_platform = sub { return 1; };

    my $req = {
        Getargshash => {
            zen_extensions => 'true',
        },
    };

    my $instance = test_func($req);
    ok(ref ($instance) eq 'Handler::Api::UFeed::Feed1PP', 'Expected Feed1PP instance');
}

sub test_get_undef_instance : Test(3) {
    my $self = shift;

    *test_func = \&Handler::Api::UFeed::instance;

    no warnings qw(redefine experimental::smartmatch);
    local *MordaX::Utils::options = sub { return 0; };
    local *MordaX::Type::is_api_search_2_only = sub { return 1; };
    local *MordaX::Type::is_app_platform = sub { return 1; };

    my $req = {};

    my $instance = test_func($req);
    ok(!defined $instance, 'Expected undefined instance');

    $req = {
        Getargshash => {
            zen_extensions => 'true',
            zen_switch => 1,
        },
    };
    $instance = test_func($req);
    ok(!defined $instance, 'Expected undefined instance');

    $req = {
        Getargshash => {
            zen_switch => 1,
        },
    };
    $instance = test_func($req);
    ok(!defined $instance, 'Expected undefined instance');
}

1;
