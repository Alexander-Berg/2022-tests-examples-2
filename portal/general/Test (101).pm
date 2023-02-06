package MordaX::HTTP;
use subs 'rand';

package MordaX::HTTP::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::HTTP;
use MordaX::Logit qw(logit dmp);

sub _redefine_object : Test(startup) {
}

sub make_fixture : Test(setup) {
    my $self = shift;

    $self->{http} = bless {}, 'MordaX::HTTP';

    %MordaX::HTTP::probabilities = ();
}

sub test_retries_more_retries : Test(2) {
    my $self = shift;

    my $alias = 'test_delete_req';

    my $sub_call_expect = {
        doretry => 1,
    };
    our $sub_call_got = {};

    no warnings "redefine";
    local *MordaX::HTTP::doretry  = sub {
        $sub_call_got->{doretry}++;
    };
    my $req_info = {
        retnum => 0,
        retries => 1,
    };

    ok($self->{http}->run_next_try($req_info));
    is_deeply($sub_call_got, $sub_call_expect);
}

sub test_progressive_exist_req : Test(2) {
    my $self = shift;

    my $alias = 'test_delete_req';

    my $sub_call_expect = {};
    our $sub_call_got = {};

    no warnings "redefine";
    local *MordaX::HTTP::doretry  = sub {
        $sub_call_got->{doretry}++;
    };
    my $req_info = {
        retnum => 1,
        retries => 1,
        progressive => 1,
        reqs => [
            {index => 0}
        ],
    };

    ok($self->{http}->run_next_try($req_info));
    is_deeply($sub_call_got, $sub_call_expect);
}

sub test_progressive_no_reqs : Test(2) {
    my $self = shift;

    my $alias = 'test_delete_req';

    my $sub_call_expect = {};
    our $sub_call_got = {};

    no warnings "redefine";
    local *MordaX::HTTP::doretry  = sub {
        $sub_call_got->{doretry}++;
    };
    my $req_info = {
        retnum => 1,
        retries => 1,
        progressive => 1,
        reqs => [
        ],
    };

    ok($self->{http}->run_next_try($req_info) == 0);
    is_deeply($sub_call_got, $sub_call_expect);
}

sub test_yet_another_retry : Test(2) {
    my $self = shift;

    my $data_subrequest_error = {
        expect => {
            retnum => 0,
            timeout => 10, 
        }
    };

    my $sub_call = {
        expect => {
            subrequest_error => 1,
            stop_req => 1,
            log_req_timings => 1,
        },
        got => {
            subrequest_error => 0,
            stop_req => 0,
            log_req_timings => 0,
        }
    };

    no warnings "redefine";
    local *MP::Logit::subrequest_error = sub($;@) {
        $data_subrequest_error->{got} = {
            retnum => $_[1]->{retnum},
            timeout => $_[1]->{timeout}
        };
        $sub_call->{got}->{subrequest_error}++;
    };
    local *MordaX::HTTP::stop_req  = sub {
        $sub_call->{got}->{stop_req}++;
    };
    local *MordaX::HTTP::log_req_timings = sub {
        $sub_call->{got}->{log_req_timings}++
    };

    my $req_info = {
        retries => 1,
        timeout => 10
    };
    my $req = {
        curl_object => '',
        start => '111',
        index => 0,
    };

    my $error = 'test yet_another_retry';

    $self->{http}->stop_req_and_log_error($req_info, $req, $error);
    is_deeply(
        $data_subrequest_error->{got},
        $data_subrequest_error->{expect}
    );
    is_deeply($sub_call->{got}, $sub_call->{expect});
}

sub test_req_undef : Test(1) {
    my $self = shift;

    my $sub_call = {
        expect => {
            subrequest_error => 0,
            stop_req => 0,
            log_req_timings => 0,
        },
        got => {
            subrequest_error => 0,
            stop_req => 0,
            log_req_timings => 0,
        }
    };

    no warnings "redefine";
    local *MP::Logit::subrequest_error = sub($;@) {
        $sub_call->{got}->{subrequest_error}++;
    };
    local *MordaX::HTTP::stop_req  = sub {
        $sub_call->{got}->{stop_req}++;
    };
    local *MordaX::HTTP::log_req_timings = sub {
        $sub_call->{got}->{log_req_timings}++
    };

    my $req_info = {
        retnum => 0,
        retries => 1,
        timeout => 10
    };
    my $req = undef;

    my $error = 'test yet_another_retry';

    $self->{http}->stop_req_and_log_error($req_info, $req, $error);
    is_deeply($sub_call->{got}, $sub_call->{expect});
}

sub test_last_retry : Test(2) {
    my $self = shift;

    my $data_subrequest_error = {
        expect => {
            retnum => 'fatal',
            timeout => 10, 
        }
    };

    my $sub_call = {
        expect => {
            subrequest_error => 1,
            stop_req => 1,
            log_req_timings => 1,
        },
        got => {
            subrequest_error => 0,
            stop_req => 0,
            log_req_timings => 0,
        }
    };

    no warnings "redefine";
    local *MP::Logit::subrequest_error = sub($;@) {
        $data_subrequest_error->{got} = {
            retnum => $_[1]->{retnum},
            timeout => $_[1]->{timeout}
        };
        $sub_call->{got}->{subrequest_error}++;
    };
    local *MordaX::HTTP::stop_req  = sub {
        $sub_call->{got}->{stop_req}++;
    };
    local *MordaX::HTTP::log_req_timings = sub {
        $sub_call->{got}->{log_req_timings}++
    };

    my $req_info = {
        retries => 1,
        timeout => 10
    };
    my $req = {
        curl_object => '',
        start => '111',
        index => 1,
    };

    my $error = 'test yet_another_retry';

    $self->{http}->stop_req_and_log_error($req_info, $req, $error);
    is_deeply(
        $data_subrequest_error->{got},
        $data_subrequest_error->{expect}
    );
    is_deeply($sub_call->{got}, $sub_call->{expect});
}

sub test_progressive_logging : Test(4) {
    my $self = shift;

    my $data_subrequest_error = {};

    my $sub_call = {
        expect => {
            subrequest_error => 0,
        },
        got => {
            subrequest_error => 0,
        }
    };

    no warnings "redefine";
    local *MP::Logit::subrequest_error = sub($;@) {
        $sub_call->{got}->{subrequest_error}++;
    };
    local *MordaX::HTTP::stop_req  = sub {};
    local *MordaX::HTTP::log_req_timings = sub {};

    my $req_info = {
        retries => 1,
        timeout => 10,
        progressive => 1,
    };
    my $req = {
        curl_object => '',
        start => '111',
        index => 1,
    };

    my $error = 'test yet_another_retry';

    $self->{http}->stop_req_and_log_error($req_info, $req, $error);
    is(
        $req_info->{subrequest_error}[0]{params}{index},
        $req->{index},
    );
    is(
        $req_info->{subrequest_error}[0]{params}{timeout},
        $req_info->{timeout},
    );
    is(
        $req_info->{subrequest_error}[0]{text_error},
        $error,
    );
    is_deeply($sub_call->{got}, $sub_call->{expect});
}

sub test_log_error_progressive : Test(3) {
    my $self = shift;

    my $data_subrequest_error = [];

    no warnings "redefine";
    local *MP::Logit::subrequest_error = sub($;@) {
        push( 
              @{$data_subrequest_error},
              {
                  alias => $_[0],
                  params => $_[1],
                  text_error => $_[2],
              }
        );
    };
    local *MordaX::HTTP::stop_req  = sub {};
    local *MordaX::HTTP::log_req_timings = sub {};

    my $req_info = {
        alias => 'test',
        retries => 1,
        timeout => 10,
        progressive => 1,
        subrequest_error => [
            {
                params => {
                    index => 0,
                },
                text_error => 'text_error',
            },
        ]
    };

    $self->{http}->log_error_progressive($req_info);
    is(
        $data_subrequest_error->[0]{alias},
        $req_info->{alias},
    );
    is($data_subrequest_error->[0]{params}{retnum}, 0);
    is($data_subrequest_error->[0]{params}{timeout}, 20);
}

sub test_log_error_progressive_fatal : Test(6) {
    my $self = shift;

    my $data_subrequest_error = [];

    no warnings "redefine";
    local *MP::Logit::subrequest_error = sub($;@) {
        push( 
              @{$data_subrequest_error},
              {
                  alias => $_[0],
                  params => $_[1],
                  text_error => $_[2],
              }
        );
    };
    local *MordaX::HTTP::stop_req  = sub {};
    local *MordaX::HTTP::log_req_timings = sub {};

    my $req_info = {
        alias => 'test',
        retries => 1,
        timeout => 10,
        progressive => 1,
        subrequest_error => [
            {
                params => {
                    index => 0,
                },
                text_error => 'text_error1',
            },
            {
                params => {
                    index => 1,
                },
                text_error => 'text_error2',
            },
        ]
    };

    $self->{http}->log_error_progressive($req_info);
    is($data_subrequest_error->[0]{params}{retnum}, 0);
    is($data_subrequest_error->[0]{params}{timeout}, 20);
    is($data_subrequest_error->[1]{params}{retnum}, 'fatal');
    is($data_subrequest_error->[1]{params}{timeout}, 10);
    is($data_subrequest_error->[0]{text_error}, $req_info->{subrequest_error}[0]{text_error});
    is($data_subrequest_error->[1]{text_error}, $req_info->{subrequest_error}[1]{text_error});
}

sub test_can_retry : Test(5) {
    my $self = shift;

    *MordaX::HTTP::rand = sub {
        return 0.5;
    };

    my $req_info = {
        alias   => 'test',
        retnum  => 0,
        retries => 1,
        smart_retry => 1,
    };
    $MordaX::HTTP::probabilities{test} = 0.6;
    ok($self->{http}->can_retry($req_info));
    $MordaX::HTTP::probabilities{test} = 0.501;
    ok($self->{http}->can_retry($req_info));
    $MordaX::HTTP::probabilities{test} = 0.499;
    ok($self->{http}->can_retry($req_info) == 0);
    $MordaX::HTTP::probabilities{test} = 0;
    ok($self->{http}->can_retry($req_info) == 0);
    $MordaX::HTTP::probabilities{test} = 1;
    ok($self->{http}->can_retry($req_info));
}

sub test_probability_max_success: Test(1) {
    my $self = shift;

    my $req_info = {
        alias   => 'test',
        retnum  => 0,
        retries => 1,
    };
    $MordaX::HTTP::probabilities{test} = 1;
    $self->{http}->calculation_of_success_probability($req_info, 1);
    ok($MordaX::HTTP::probabilities{test} == 1);
}

sub test_probability_zero_fail: Test(1) {
    my $self = shift;

    my $req_info = {
        alias   => 'test',
        retnum  => 0,
        retries => 1,
    };
    $MordaX::HTTP::probabilities{test} = 0;
    $self->{http}->calculation_of_success_probability($req_info, 0);
    ok($MordaX::HTTP::probabilities{test} == 0);
}

sub test_two_success: Test(1) {
    my $self = shift;

    my $req_info = {
        alias   => 'test',
        retnum  => 0,
        retries => 1,
    };
    $self->{http}->calculation_of_success_probability($req_info, 1);
    my $one = $MordaX::HTTP::probabilities{test};
    $self->{http}->calculation_of_success_probability($req_info, 1);
    my $two = $MordaX::HTTP::probabilities{test};
    ok($one < $two);
}

sub test_two_fail: Test(1) {
    my $self = shift;

    my $req_info = {
        alias   => 'test',
        retnum  => 0,
        retries => 1,
    };
    $self->{http}->calculation_of_success_probability($req_info, 1);
    $self->{http}->calculation_of_success_probability($req_info, 0);
    my $one = $MordaX::HTTP::probabilities{test};
    $self->{http}->calculation_of_success_probability($req_info, 0);
    my $two = $MordaX::HTTP::probabilities{test};
    ok($one > $two);
}

sub test_two_success_one_fail: Test(2) {
    my $self = shift;

    my $req_info = {
        alias   => 'test_two_success_one_fail',
        retnum  => 0,
        retries => 1,
    };
    $self->{http}->calculation_of_success_probability($req_info, 1);
    my $one = $MordaX::HTTP::probabilities{test_two_success_one_fail};
    $self->{http}->calculation_of_success_probability($req_info, 1);
    my $two = $MordaX::HTTP::probabilities{test_two_success_one_fail};
    $self->{http}->calculation_of_success_probability($req_info, 0);
    my $three = $MordaX::HTTP::probabilities{test_two_success_one_fail};
    ok($one < $two);
    ok($two > $three);
}

sub test_add_antirobot_header : Test(4) {
    my $self = shift;

    no warnings qw(redefine);
    *add_antirobot_header = \&MordaX::HTTP::add_antirobot_header;

    #
    # === disable_forward_antirobot_header = 1
    #
    local *MordaX::Options::options = sub {
        return 1 if ($_[0] eq 'disable_forward_antirobot_header');
    };
    add_antirobot_header($self, {});
    is(exists $self->{antirobot_headers}, '', 'disable_forward_antirobot_header = 1');

    #
    # === eval MordaX::Req::header failed
    #
    local *MordaX::Options::options = sub {
        return 0 if ($_[0] eq 'disable_forward_antirobot_header');
    };
    add_antirobot_header($self, {});
    is(exists $self->{antirobot_headers}, '', 'eval MordaX::Req::header failed');

    #
    # === MordaX::Req::header("X-Antirobot-Robotness-Y") returned undef
    #
    local *MordaX::Req::header = sub {
        return undef if ($_[1] eq 'X-Antirobot-Robotness-Y');
    };
    add_antirobot_header($self, {});
    is(exists $self->{antirobot_headers}, '', 'MordaX::Req::header("X-Antirobot-Robotness-Y") returned undef');

    #
    # === MordaX::Req::header("X-Antirobot-Robotness-Y") returned value
    #
    *MordaX::Req::header = sub {
        return 'true' if ($_[1] eq 'X-Antirobot-Robotness-Y');
    };
    add_antirobot_header($self, {});
    is_deeply($self->{antirobot_headers}, [{'name' => 'X-Antirobot-Robotness-Y', 'value' => 'true'}], 'MordaX::Req::header("X-Antirobot-Robotness-Y") returned value');
}

sub test_push_headers : Test(3) {
    no warnings qw(redefine);
    *push_headers = \&MordaX::HTTP::push_headers;

    #
    # === empty $input
    #
    my $result->{headers} = [];
    my $input = [];

    push_headers($result, $input);
    is_deeply($result->{headers}, [], 'empty $input');

    #
    # === $input = X-Antirobot-Robotness-Y: true
    #
    $input = [{'name' => 'X-Antirobot-Robotness-Y', 'value' => 'true'}];

    push_headers($result, $input);
    is_deeply($result->{headers}, ['X-Antirobot-Robotness-Y: true'], '$input = X-Antirobot-Robotness-Y: true');

    #
    # === $input = HOST: yandex.ru
    #
    $result->{headers} = [];
    $input = [{'name' => 'HOST', 'value' => 'yandex.ru'}];

    push_headers($result, $input);
    is_deeply($result, {'headers' => ['HOST: yandex.ru'], 'hostpassed' => 1}, '$input = HOST: yandex.ru');
}

1;
