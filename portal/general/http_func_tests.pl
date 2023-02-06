#!/usr/bin/perl

#Перед ззапуском задать переменную окружения PERL5LIB=<путь до lib>
#PERL5LIB=/opt/www/morda-v84d5/lib perl simple_http.pl
#
#Поднять сервер simple_http_server.pl
#В HTTP.pm, в ф-и addreq, добавить в url параметр try
#$req_info->{'url'} .= '&try=' . $req_info->{retnum};

use strict;
use warnings;
use utf8;

use Data::Dumper;
use MordaX::HTTP;
use Test::Most;

my $type = $ARGV[0];
my $requests = _get_requests();
_connon_fire($requests);



sub _connon_fire {
    my $ammo = shift;

    for my $request (@$ammo) {
        my $response;

        my $log_errors = {};
        no warnings "redefine";
        *MP::Logit::subrequest_error = sub($;@) {
            my ($alias, $params, $text) = @_;

            my $timeout = $params->{timeout};
            my $retnum = $params->{retnum};
            $log_errors->{$alias}{$retnum} = {
                retnum => $retnum,
                text   => $text,
                timeout => $timeout,
            };
        };

        my $http_agent = MordaX::HTTP->new({});
        my $testing_info = delete $request->{testing_info};
        my @args = ();
        for my $try (keys %$testing_info) {
            for my $args_try_key (keys %{$testing_info->{$try}}) {
                my $args_try_value = $testing_info->{$try}{$args_try_key};
                push (@args, $args_try_key . $try . '='  . $args_try_value);
            }
        }
        $request->{url} = $request->{url} . '?' . join('&', @args);
        $http_agent->add(
            %$request,
        );
        my $alias = $request->{alias};
        my $ri = $http_agent->result_req_info($alias);

        is_deeply($log_errors->{$alias}, $request->{exp}{log_error}, $alias . '-logging subreq');
        is($ri->{success}, $request->{exp}{success}, $alias . '-succes');
        is($ri->{error}, $request->{exp}{error}, $alias . '-error');

        sleep(1);
    }
}

done_testing();

sub _get_requests {
    return [
        {
            #первый 500 через 150мл, второй таймаут;
            'alias' => 'test1',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 500,
                }, 
                1 => {
                    wait => 150_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => 0,
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 500 через 150мл, второй 500 через 40;
            'alias' => 'test2',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 500,
                }, 
                1 => {
                    wait => 40_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                    1 => {
                        retnum => '1',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 500 через 150мл, второй 500 через 70;
            'alias' => 'test3',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 500,
                }, 
                1 => {
                    wait => 70_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                    0 => {
                        retnum => '0',
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый таймаут 210мл, второй 500 через 70;
            'alias' => 'test4',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 210_000,
                    status => 200,
                }, 
                1 => {
                    wait => 70_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.2,
                        text => 'request timed out',
                    },
                    1 => {
                        retnum => '1',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 150 мл  200, второй 30 млс 500;
            'alias' => 'test5',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 200,
                }, 
                1 => {
                    wait => 30_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    1 => {
                        retnum => '1',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 1,
                error => 0,
            },
        },
        {
            #первый и второй таймауты;
            'alias' => 'test6',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 210_000,
                    status => 200,
                }, 
                1 => {
                    wait => 110_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                    0 => {
                        retnum => '0',
                        timeout => 0.2,
                        text => 'request timed out',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 500 до запуска второго, второй 200 через 50;
            'alias' => 'test7',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 30_000,
                    status => 500,
                }, 
                1 => {
                    wait => 30_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 1,
                error => 0,
            },
        },
        {
            #первый 500 до запуска второго, второй 500 через 50;
            'alias' => 'test8',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 30_000,
                    status => 500,
                }, 
                1 => {
                    wait => 30_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 500 до запуска второго, второй таймаут;
            'alias' => 'test9',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 30_000,
                    status => 500,
                }, 
                1 => {
                    wait => 110_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 200 через 150, второй таймаут;
            'alias' => 'test10',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 200,
                }, 
                1 => {
                    wait => 110_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            #первый 200 через 150, второй 200 через 60;
            'alias' => 'test11',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 200,
                }, 
                1 => {
                    wait => 60_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            #первый 200 через 150, второй 500 через 70;
            'alias' => 'test12',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 200,
                }, 
                1 => {
                    wait => 70_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            #первый 500 через 150, второй 200 через 30;
            'alias' => 'test13',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 150_000,
                    status => 500,
                }, 
                1 => {
                    wait => 30_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            #первый таймаут, второй 200 через 30;
            'alias' => 'test14',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 210_000,
                    status => 200,
                }, 
                1 => {
                    wait => 30_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            #первый 200 через 50, второй не запускается;
            'alias' => 'test15',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 50_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            #первый 500 до запуска второго, второй 200 через 50;
            'alias' => 'test16',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 30_000,
                    status => 500,
                }, 
                1 => {
                    wait => 50_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 1,
                error => 0,
            },
        },
        {
            #первый таймаут, второй через 50 мл 200, progressive=0;
            'alias' => 'test17',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 0,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 210_000,
                    status => 200,
                }, 
                1 => {
                    wait => 50_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                },
                success => 1,
                error => 0,
            },
        },
        {
            #первый таймаут, второй тоже таймаут, progressive=0;
            'alias' => 'test18',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 0,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 110_000,
                    status => 200,
                }, 
                1 => {
                    wait => 110_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 50 мл  200, второго не будет;
            'alias' => 'test19',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 0,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 50_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            #первый таймаут, второй 500, progressive=0;
            'alias' => 'test19',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 0,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 110_000,
                    status => 200,
                }, 
                1 => {
                    wait => 30_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 500, второй таймаут, progressive=0;
            'alias' => 'test21',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 0,
            'keep_alive' => 0,
            testing_info => {
                1 => {
                    wait => 110_000,
                    status => 200,
                }, 
                0 => {
                    wait => 30_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 500, второй 500, progressive=0;
            'alias' => 'test22',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 0,
            'keep_alive' => 0,
            testing_info => {
                1 => {
                    wait => 30_000,
                    status => 500,
                }, 
                0 => {
                    wait => 30_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 0,
                error => 1,
            },
        },
        {
            #первый 500, второй через 50 мл 200, progressive=0;
            'alias' => 'test23',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 1,
            'progressive' => 0,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 20_000,
                    status => 500,
                }, 
                1 => {
                    wait => 50_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 1,
                error => 0,
            },
        },
        {
            # Три трая. первый 200 через 250, второй и третий таймауты;
            'alias' => 'test24',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 2,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 250_000,
                    status => 200,
                }, 
                1 => {
                    wait => 210_000,
                    status => 200,
                }, 
                2 => {
                    wait => 110_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => undef,
                success => 1,
                error => 0,
            },
        },
        {
            # Три трая. первый 200 через 260, второй 500 через 150, третий таймаут;
            'alias' => 'test25',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 2,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 260_000,
                    status => 200,
                }, 
                1 => {
                    wait => 150_000,
                    status => 500,
                }, 
                2 => {
                    wait => 110_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    1 => {
                        retnum => '1',
                        timeout => 0.2,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 1,
                error => 0,
            },
        },
        {
            # Три трая. первый 500 через 230, второй 200 через 150, третий через 20 500 ;
            'alias' => 'test26',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 2,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 230_000,
                    status => 500,
                }, 
                1 => {
                    wait => 150_000,
                    status => 200,
                }, 
                2 => {
                    wait => 20_000,
                    status => 500,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.3,
                        text => 'Bad status code response: code(500)',
                    },
                    2 => {
                        retnum => '2',
                        timeout => 0.1,
                        text => 'Bad status code response: code(500)',
                    },
                },
                success => 1,
                error => 0,
            },
        },
        {
            # Три трая. все таймауты;
            'alias' => 'test27',
            'url' => 'http://127.0.0.1:5050/yabs',
            'timeout' => 0.1,
            'retries' => 2,
            'progressive' => 1,
            'keep_alive' => 0,
            testing_info => {
                0 => {
                    wait => 310_000,
                    status => 200,
                }, 
                1 => {
                    wait => 210_000,
                    status => 200,
                }, 
                2 => {
                    wait => 110_000,
                    status => 200,
                }, 
            },
            exp => {
                log_error => {
                    0 => {
                        retnum => '0',
                        timeout => 0.3,
                        text => 'request timed out',
                    },
                    1 => {
                        retnum => '1',
                        timeout => 0.2,
                        text => 'request timed out',
                    },
                    fatal => {
                        retnum => 'fatal',
                        timeout => 0.1,
                        text => 'request timed out',
                    },
                },
                success => 0,
                error => 1,
            },
        },
    ];
}
