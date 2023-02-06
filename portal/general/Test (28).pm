package MordaX::AppHost::Base::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use Test::More;
use Scalar::Util qw(weaken);
use Sub::Name qw(subname);
use List::Util qw(pairs);

use MordaX::Config;
use MordaX::Conf;

use NAppHostProtocol::TAnswer;
use NAppHostProtocol::TServiceResponse;
use MP::NAppHost qw(:compress);

# fix logit debug
{
    no warnings qw(redefine);
    *MordaX::Logit::logit = sub {};
    *MordaX::Logit::LOGIT_OK = \1;
}

sub apphost_class {'MordaX::AppHost::FakeTest'}

sub graph_id {'fake'}

sub mordax_config_mock {
    my $self = shift;
    $self->{mordax_config}->{ $_->[0] } = $_->[1] for pairs @_;
    return;
}

sub make_response {
    my ($self, $type) = @_;
    $type //= 'fake_answer_type';
    my $data = '{"ok" : 1}';
    encode_napphost_data(NAPPHOST_CODEC_LZ4, $data);
    my $answer = NAppHostProtocol::TAnswer->new();
    $answer->set_Data($data);
    $answer->set_Type($type);
    $answer->set_SourceName("TEST");
    my $res = NAppHostProtocol::TServiceResponse->new();
    $res->add_Answers($answer);
    return scalar $res->pack;
}

sub set_tests {
    my $self = shift;
    my $tests = $self->{tests} = {
        class_methods => {
            type        => 'fake_type',
            answer_type => 'fake_answer_type',
            source_name => 'fake_source_name',
        },
        timeout => {
            ok => [1, 50, 20, 10, 5],
            not_ok => [0, 51, 60, 100, 3600, -1],
        },
        retries => {
            ok => [0, 1, 2],
            not_ok => [-1, 3, 6, 10],
        },
        madm_conf => {
            add => [
                { retries    => 1,  addr => '', },
                { timeout_ms => 10, addr => "http://x.ru", retries => -1 },
                { timeout_ms => -1, addr => "", retries => -1 },
            ],
            expected => {
                retries => 1,
                addr    => "http://x.ru",
                timeout => 10,
            },
        },
        alias => "apphost_" . $self->graph_id,
        ctx   => {
            args => [{
                    Requestid     => "123",
                    time          => 10,
                    GeoByDomainIp => 213,
                    Locale        => 'ru',
                    api_search    => 2,
                    MordaContent  => 'touch',
                    MordaZone     => 'ru',
                    extra_arg     => 1,
                    UserDevice    => {
                        app_version  => 9090900,
                        app_platform => 'iphone',
                        dpi          => 1.5,
                    },
                    timezone => 'UTC',
                    GeoDetection => { 1 => 2 },
            }],
            expected => {
                GeoDetection  => { 1 => 2 },
                Requestid     => "123",
                time          => 10,
                GeoByDomainIp => 213,
                Locale        => 'ru',
                api_search    => 2,
                MordaContent  => 'touch',
                MordaZone     => 'ru',
                UserDevice    => {
                    app_version  => 9090900,
                    app_platform => 'iphone',
                    dpi          => 1.5,
                },
                AddMode  => 0,
                timezone => 'UTC',
            },
        },
        encode_ctx => {
            ctx => { some => 'data' },
            expected => "\x{12}\x{39}\x{0a}\x{10}\x{66}\x{61}\x{6b}\x{65}\x{5f}\x{73}\x{6f}\x{75}\x{72}\x{63}\x{65}\x{5f}\x{6e}\x{61}\x{6d}\x{65}\x{12}\x{09}\x{66}\x{61}\x{6b}\x{65}\x{5f}\x{74}\x{79}\x{70}\x{65}\x{1a}\x{1a}\x{02}\x{0f}\x{00}\x{00}\x{00}\x{00}\x{00}\x{00}\x{00}\x{f0}\x{00}\x{7b}\x{22}\x{73}\x{6f}\x{6d}\x{65}\x{22}\x{3a}\x{22}\x{64}\x{61}\x{74}\x{61}\x{22}\x{7d}",
        },
    };

    return $tests;
}

sub config_setup {
    my $self = shift;
    $self->mordax_config_mock(
        app_host => {
            fake_addr    => "http://ya.ru",
            fake_timeout => 50,
            fake_retries => 1,
        },
    );
    return;
}

sub simple_obj {
    my ($self)   = @_;
    my $graph_id = $self->graph_id;
    my $class    = $self->apphost_class;
    my $http     = HTTP::Test->new();
    return $class->new($graph_id, $http);
}

sub set_tests_startup : Test(startup) { shift->set_tests() }

sub config_setup_startup : Test(startup) { shift->config_setup() }

sub disable_testing_instance : Test(startup) {
    $MordaX::Config::TestingInstance = 0;
    return;
}

sub redefine_mordax_conf : Test(startup) {
    no warnings qw(redefine);
    no strict qw(refs);
    weaken(my $self = shift);

    if (*{'MordaX::Conf::get'}{CODE}) {
        my $real_get = \&MordaX::Conf::get;
        *MordaX::Conf::get = sub {
            if (exists $self->{mordax_config}->{ $_[1] }) {
                return $self->{mordax_config}->{ $_[1] };
            }
            else {
                goto &$real_get;
            }
        };
    }
    else {
        *MordaX::Conf::get = subname 'MordaX::Conf::get' => sub {
            if (exists $self->{mordax_config}->{ $_[1] }) {
                return $self->{mordax_config}->{ $_[1] };
            }
            else {
                return (shift)->next::method(@_);
            }
        };
    }
    return;
}

sub requier : Test(startup => no_plan) {
    my $self = shift;
    if (ref $self ne __PACKAGE__) {
        use_ok($self->apphost_class);
    }
    return;
}


sub class_methods : Tests {
    my ($self)  = @_;
    my $methods = $self->{tests}->{class_methods};
    my $class   = $self->apphost_class;
    for my $m (keys %$methods) {
        my $expected = $methods->{$m};
        if ($expected) {
            is($class->$m, $expected);
        }
    }
    return;
}

sub timeout : Tests {
    my ($self) = @_;
    my $tests  = $self->{tests}->{timeout};
    my $class  = $self->apphost_class;
    ok($class->timeout_ok($_),  "timeout = $_") for @{ $tests->{ok} };
    ok(!$class->timeout_ok($_), "timeout = $_") for @{ $tests->{not_ok} };
    return;
}

sub retries : Tests {
    my ($self) = @_;
    my $tests  = $self->{tests}->{retries};
    my $class  = $self->apphost_class;
    ok($class->retries_ok($_),  "retries = $_") for @{ $tests->{ok} };
    ok(!$class->retries_ok($_), "retries = $_") for @{ $tests->{not_ok} };
    return;
}

sub madm_conf : Tests {
    my ($self) = @_;
    my $test   = $self->{tests}->{madm_conf};
    my $class  = $self->apphost_class;
    for my $row (@{ $test->{add} }) {
        $class->add_madm_conf($row);
    }
    is_deeply($class->get_madm_conf, $test->{expected});
    $class->clean_madm_conf();
    is_deeply($class->get_madm_conf, {}, "after clean");
    return;
}

sub creation : Tests {
    my ($self)   = @_;
    my $app_host = $self->simple_obj();
    isa_ok($app_host, $self->apphost_class);
    is($app_host->{id},      $self->graph_id);
    is($app_host->{retries}, 1);
    is($app_host->{timeout}, 0.05);
    is($app_host->{url},     "http://ya.ru");
    isa_ok($app_host->{http}, "HTTP::Test");
    return;
}

sub alias : Tests {
    my ($self)   = @_;
    my $app_host = $self->simple_obj();
    my $expected = $self->{tests}->{alias};
    is($app_host->alias(), $expected);
    return;
}

sub ctx : Tests {
    my ($self)   = @_;
    my $app_host = $self->simple_obj();
    my $test     = $self->{tests}->{ctx};
    my $got      = $app_host->ctx(@{ $test->{args} });
    is_deeply($got, $test->{expected});
    return;
}

sub _encode_ctx : Tests {
    my ($self)   = @_;
    my $app_host = $self->simple_obj();
    my $test     = $self->{tests}->{encode_ctx};
    my $got      = $app_host->_encode_ctx($test->{ctx});
    is($$got, $test->{expected});
    return;
}

sub send : Tests {
    my ($self)   = @_;
    my $app_host = $self->simple_obj();
    my $ctx_test = $self->{tests}->{encode_ctx};
    $app_host->send($ctx_test->{ctx}) for (1 .. 3);
    my $http = $app_host->{http};
    ok(@{ $http->{requests} } == 1, "send only one request");
    my $expected = {
        alias              => $app_host->alias(),
        url                => "http://ya.ru",
        timeout            => 0.05,
        can_v6             => 0,
        retries            => 1,
        progressive        => 0,
        post               => 1,
        gzip               => 0,
        post_data          => \$ctx_test->{expected},
        no_ssrf_protection => 1,
        slow               => 1,
        keepalive_disable  => 1,
        response_ref       => 1,

    };
    is_deeply($http->{requests}->[0], $expected);
    return;
}

sub response : Tests {
    my ($self) = @_;
    my $app_host = $self->simple_obj();
    $app_host->send({});
    my $http = $app_host->{http};
    my $res  = $self->make_response();
    $http->{result_req_info} = {
        success          => 1,
        response_content => \$res,
    };
    my $got = $app_host->response();
    is_deeply($got, { ok => 1 });
    return;
}

# Так как класс MordaX::AppHost::Base - базовый, то некоторые методы
# надо обязательно переопределять. Данный класс ниже как раз выполняет эту
# роль, чтобы протестировать базовые методы, которые зависят от методов,
# которые необходимо переопределить.
package MordaX::AppHost::FakeTest;

use base qw(MordaX::AppHost::Base);

sub type { 'fake_type' }

sub source_name { 'fake_source_name' }

sub answer_type { 'fake_answer_type'  }

package HTTP::Test;

sub new { bless {}, shift; }

sub add {
    my ($self, %args) = (shift, @_);
    push @{ $self->{requests} }, \%args;
    return 1;
}

sub result_req_info {
    my $self = shift;
    return $self->{result_req_info};
}

1;
