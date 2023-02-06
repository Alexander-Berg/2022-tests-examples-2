package MP::Tvm::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use MTH;

use base qw(Test::Class);

use MP::Logit qw(dmp);

use Test::More;

use Scalar::Util qw(weaken);

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok('MP::Tvm');

    no warnings 'redefine';
    *MordaX::HTTP::add = sub {};
    *MP::Tvm::check_tvmtool_config = sub {return 1};
    use warnings 'redefine';

    return;
}

sub initialization: Tests {
    my $req = {'time' => time};
    mock_options();
    MP::Tvm::_test_clean_cache();
    is_deeply(MP::Tvm::_test_show_cache(), {}, 'empty cache');
    is(MP::Tvm::_get_good_tvm_cache($req), undef, 'no good cache');
    is(MP::Tvm::_get_tvm_cache($req), undef, 'no any cache');

    return;
}

sub set_get_cache: Tests {
    my $req = {'time' => time};
    mock_options();
    MP::Tvm::_set_tvm_cache($req, {ttt => 111});
    is_deeply(MP::Tvm::_test_show_cache(), {tvm_cached_data=>{ttt=>111}, tvm_cache_exp_time => $req->{time} + MP::Tvm::TVM_TICKETS_TTL()}, 'check for good cache');
    is_deeply(MP::Tvm::_get_tvm_cache(), {ttt=>111}, 'get cache');
    is_deeply(MP::Tvm::_get_good_tvm_cache($req), {ttt=>111}, 'get good cache');

    $req->{time} += MP::Tvm::TVM_TICKETS_TTL() + 1;
    is_deeply(MP::Tvm::_get_good_tvm_cache($req), undef, 'cache expired good cache');
    return;
}

sub get_tickets_start_request: Tests {
    my $req = {'time' => time};
    mock_options();

    no warnings 'redefine';
    local *MP::Tvm::check_tvmtool_config = sub {return 0};
    use warnings 'redefine';

    is(MP::Tvm::get_tickets_start_request($req), 0, 'bad config');

    no warnings 'redefine';
    local *MP::Tvm::check_tvmtool_config = sub {return 1};
    use warnings 'redefine';

    MP::Tvm::_test_clean_cache();
    $req = {'time' => time}; # flush Once_req
    is(MP::Tvm::get_tickets_start_request($req), 1, 'tvm request started: no option enable_tvmtool_cache_by_host');
    mock_options(['enable_tvmtool_cache_by_host']);

    $req = {'time' => time}; # flush Once_req
    is(MP::Tvm::get_tickets_start_request($req), 1, 'tvm request started: no good cache');

    $req = {'time' => time}; # flush Once_req
    MP::Tvm::_set_tvm_cache($req, {ttt => 111});
    is(MP::Tvm::get_tickets_start_request($req), 0, 'tvm request not started: have good cache');

    $req = {'time' => time}; # flush Once_req
    $req->{time} += MP::Tvm::TVM_TICKETS_TTL() - 10; # good cache
    is(MP::Tvm::get_tickets_start_request($req), 0, 'tvm request not started: have good cache');

    $req = {'time' => time}; # flush Once_req
    $req->{time} += MP::Tvm::TVM_TICKETS_TTL() + 1; # stale cache
    is(MP::Tvm::get_tickets_start_request($req), 1, 'tvm request not started: cache expired');
}

sub get_tvm2_ticket: Tests {
    my $req = {'time' => time};

    my $good_cache = {ttt => {ticket => 111}};
    MP::Tvm::_set_tvm_cache($req, $good_cache);

    is(MP::Tvm::get_tvm2_ticket($req, 'ttt'), 111);

    my $error;
    my $warning;
    no warnings 'redefine';
    local *MP::Tvm::logit = sub {
        $error = $_[1] if $_[0] eq 'interr';
        $warning = $_[1] if $_[0] eq 'warning';
        return 1;
    };
    use warnings 'redefine';

    is(MP::Tvm::get_tvm2_ticket($req, 'ttt_unknown'), undef);
    is($error, 'can not get tvm ticket for service: ttt_unknown', 'check for warnings');

}

sub _get_all_tickets: Tests {
    my $req = {'time' => time};

    my $good_cache = {ttt => 111};
    MP::Tvm::_set_tvm_cache($req, $good_cache);
    is_deeply(MP::Tvm::_get_all_tickets($req), $good_cache, 'fresh tickets cache');


    $req = {'time' => time}; # flush Once_req
    $req->{time} += MP::Tvm::TVM_TICKETS_TTL() + 1; # stale cache
    my $rt_tickets = {'mock_cache'=>1};
    no warnings 'redefine';
    local *MP::Tvm::_get_tickets_process = sub {return $rt_tickets};
    use warnings 'redefine';

    is_deeply(MP::Tvm::_get_all_tickets($req), $rt_tickets, 'rt tickets');

    no warnings 'redefine';
    local *MP::Tvm::_get_tickets_process = sub {return undef};
    use warnings 'redefine';
    $req = {'time' => time}; # flush Once_req
    $req->{time} += MP::Tvm::TVM_TICKETS_TTL() + 1; # stale cache

    my $error;
    my $warning;
    no warnings 'redefine';
    local *MP::Tvm::logit = sub {
        $error = $_[1] if $_[0] eq 'interr';
        $warning = $_[1] if $_[0] eq 'warning';
        return 1;
    };
    use warnings 'redefine';
    is_deeply(MP::Tvm::_get_all_tickets($req), $good_cache, 'use any cache');
    is($warning, 'have no tvm response', 'check for warnings');
    MP::Tvm::_test_clean_cache();
    is_deeply(MP::Tvm::_get_all_tickets($req), undef, 'no cache no response');
    is($error,   'have no tvm response and any cache', 'check for interr');
}

1;
