#!/usr/bin/env perl
use strict;
use warnings;
use Test::Most 'no_plan';
# die_on_fail();

use geobase5 '5.0.1'; #поменять на на 4-ю версию для теста
# use geobase4 '3.2.5';
my $libgeobase = 'geobase5'; #поменять на namespace подключенной геолибы
# my $libgeobase = 'geobase4';

use File::Temp qw/tempfile/;
use Data::Dumper;
use Readonly;
Readonly my $DB_PATH => '/opt/www/bases/geodata50.bin';

=encoding utf8

=head1 NAME

    # libgeobase.t
    
=head1 DESCRIPTION

    # Тестирование библиотечного варианта определения геокоординат.
    # Расчитано на 4 и 5-ю версию библиотеки.

=cut

subtest 'ip yp ys set, gid 139272' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        $geobase->set_new_geolocation_used(1);
        
        my $geolocation_search_data = ($libgeobase . '::geolocation_search_data')->new();
        $geolocation_search_data->set_ip('::ffff:87.10.233.170');
        # $geolocation_search_data->set_yandex_gid('139272');
         $geolocation_search_data->set_yandex_gid('99999999');
        my $geolocation = ($libgeobase . '::geolocation')->new();
        
        my $res = $geobase->pinpoint_geolocation($geolocation_search_data, '', '', $geolocation);
        ok(defined $res, 'res defined');
        
        my $region = ($libgeobase . '::region')->new;        
        is($geolocation->region_id, 139272, 'region_id 139272');
        $geobase->region_by_id($geolocation->region_id, $region);
        is($region->name, 'Чампино', 'region name Чампино');
        is($geolocation->precision, 2, 'precision 2');
    };
die 123;

subtest 'geolocation_search_data class' => sub {
    subtest 'setters' => sub {
        subtest 'set_yandex_gid' => sub {
            #check numeric
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $warn = '';
                local $SIG{'__WARN__'} = sub { $warn .= shift };
                $search_data->set_yandex_gid('asd');
                like($warn, qr/Argument .+ isn't numeric in subroutine entry/, 'WARN: set_yandex_gid numeric check');
            };
            
            #no argument
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                eval {
                    $search_data->set_yandex_gid();
                };
                ok($@, 'empty gid exception');
                like($@, qr/Usage: ${libgeobase}::geolocation_search_data::set_yandex_gid\(self, gid\)/, 'DIE: Usage: $libgeobase::geolocation_search_data::set_yandex_gid(self, gid)');
            };
            
            #correct argument
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $yandex_gid = '1234567890';
                eval {
                    $search_data->set_yandex_gid($yandex_gid);
                };
                ok(!$@, 'correct call no exception');
                is($search_data->yandex_gid, $yandex_gid, 'get yandex_gid');
            };
        };
   
        subtest 'set_ip' => sub {
            #incorrect call
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $ip = 'asd';
                $search_data->set_ip($ip);
                is($search_data->ip(), $ip, 'get ip');
            };
            
            #no arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                eval {
                    $search_data->set_ip();
                };
                ok($@, 'empty ip exeption');
                like($@, qr/Usage: ${libgeobase}::geolocation_search_data::set_ip\(self, ip\)/, 'DIE: Usage: $libgeobase::geolocation_search_data::set_ip(self, ip)');
            };
            
            #correct
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $ip = 'asd';
                eval {
                    $search_data->set_ip($ip);
                };
                ok(!$@, 'correct call no exeption');
                is($search_data->ip, $ip, 'get ip');
            };
        };

        subtest 'set_gpauto' => sub {
            #incorrect arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $gpauto = 'asd';
                $search_data->set_gpauto($gpauto);
                is($search_data->gpauto(), $gpauto, 'get gpauto');
            };
            
            #no arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                eval {
                    $search_data->set_gpauto();
                };
                ok($@, 'empty gpauto exception');
                like($@, qr/Usage: ${libgeobase}::geolocation_search_data::set_gpauto\(self, gpauto\)/, "DIE: Usage: ${libgeobase}::geolocation_search_data::set_gpauto(self, gpauto)");
            };
            
            #correct
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $gpauto = 'asd';
                eval {
                    $search_data->set_gpauto($gpauto);
                };
                ok(!$@, 'correct call no exeption');
                is($search_data->gpauto, $gpauto, 'get gpauto');
            };
        };
        
        subtest 'set_x_forwarded_for' => sub {
            #incorrect arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $x_forwarded_for = 0x0;
                $search_data->set_x_forwarded_for($x_forwarded_for);
                is($search_data->x_forwarded_for(), $x_forwarded_for, 'get x_forwarded_for');
            };
            
            #no arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                eval {
                    $search_data->set_x_forwarded_for();
                };
                ok($@, 'empty x_forwarded_for exception');
                like($@, qr/Usage: ${libgeobase}::geolocation_search_data::set_x_forwarded_for\(self, x_forwarded_for\)/, 'DIE: Usage: ${libgeobase}::geolocation_search_data::set_x_forwarded_for(self, x_forwarded_for)');
            };
            
            #correct
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $x_forwarded_for = 0x0;
                eval {
                    $search_data->set_x_forwarded_for($x_forwarded_for);
                };
                ok(!$@, 'correct call no exeption');
                is($search_data->x_forwarded_for, $x_forwarded_for, 'get x_forwarded_for');
            };
        };

        subtest 'set_x_real_ip' => sub {
            #incorrect arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $x_real_ip = 0x0;
                $search_data->set_x_real_ip($x_real_ip);
                is($search_data->x_real_ip(), $x_real_ip, 'get x_real_ip');
            };
            
            #no arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                eval {
                    $search_data->set_x_real_ip();
                };
                ok($@, 'empty set_x_real_ip exception');
                like($@, qr/Usage: ${libgeobase}::geolocation_search_data::set_x_real_ip\(self, x_real_ip\)/, 'DIE: Usage: ${libgeobase}::geolocation_search_data::set_x_real_ip(self, x_real_ip)');
            };
            
            #correct
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $x_real_ip = 0x0;
                eval {
                    $search_data->set_x_real_ip($x_real_ip);
                };
                ok(!$@, 'correct call no exeption');
                is($search_data->x_real_ip, $x_real_ip, 'get x_real_ip');
            };
        };

        subtest 'set_user_points' => sub {
            #incorrect arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $user_points = 'blabla';
                $search_data->set_user_points($user_points);
                is($search_data->user_points(), $user_points, 'get set_user_points');
            };
            
            #no arg
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                eval {
                    $search_data->set_user_points();
                };
                ok($@, 'empty set_user_points exception');
                like($@, qr/Usage: ${libgeobase}::geolocation_search_data::set_user_points\(self, user_points\)/, 'DIE: Usage: ${libgeobase}::geolocation_search_data::set_user_points(self, user_points)');
            };
            
            #correct
            do {
                my $search_data = ($libgeobase . '::geolocation_search_data')->new;
                my $user_points = 'blabla';
                eval {
                    $search_data->set_user_points($user_points);
                };
                ok(!$@, 'correct call no exeption');
                is($search_data->user_points, $user_points, 'get user_points');
            };
        };
        #TODO сделать для следующих сеттеров
        # $search_data->set_user_points();
        # $search_data->set_override_point();
        # $search_data->set_is_trusted();
        # $search_data->set_allow_yandex();
        # $search_data->set_disable_suspected_region();        
    };
};

subtest 'pinpoint_geolocation method' => sub {
    #нарушение интерфейса не приводит к exception
    #тут вообще ничего не приводит к exception
    subtest 'unblessed geo_search_data' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        my $yp = '';
        my $ys = '';
        my $geolocation = ($libgeobase . '::geolocation')->new();
        my $warn;
        local $SIG{__WARN__} = sub {$warn .= shift};
        my $res = $geobase->pinpoint_geolocation(undef, '', '', $geolocation);
        ok(!defined $res, 'res not defined');
        like($warn, qr/search_data is not a blessed SV reference/, 'WARN: search_data is not a blessed SV reference');
        is($geolocation->region_id, -1, 'region_id -1');
    };

    subtest 'unblessed geolocation' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        my $geolocation_search_data = ($libgeobase . '::geolocation_search_data')->new();
        my $yp = '';
        my $ys = '';
        my $warn;
        local $SIG{__WARN__} = sub {$warn .= shift};
        my $res = $geobase->pinpoint_geolocation($geolocation_search_data, '', '', undef);
        ok(!defined $res, 'res not defined');
        like($warn, qr/geolocation is not a blessed SV reference/, 'WARN: geolocation is not a blessed SV reference');
    };

    subtest 'no yp ys' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        my $geolocation_search_data = ($libgeobase . '::geolocation_search_data')->new();
        my $geolocation = ($libgeobase . '::geolocation')->new();
        my $warn;
        local $SIG{__WARN__} = sub {$warn .= shift};
        my $res = $geobase->pinpoint_geolocation($geolocation_search_data, undef, undef, $geolocation);
        ok(defined $res, 'res defined');
        like($warn, qr/Use of uninitialized value in subroutine entry/, 'WARN: Use of uninitialized value in subroutine entry');
        #косяк. выдача зависит от версии
        if ($libgeobase eq 'geobase4') {
            is($geolocation->region_id, 0, 'default region_id v4 0');
        } elsif ($libgeobase eq 'geobase5') {
            is($geolocation->region_id, 10000, 'default region_id v5 10000');
        } else {
            fail('Unsupported geolib version');
        }
        is($geolocation->precision, 0, 'precision 0');
    };

    subtest 'correct and empty args' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        my $geolocation_search_data = ($libgeobase . '::geolocation_search_data')->new();
        my $yp = '';
        my $ys = '';
        my $geolocation = ($libgeobase . '::geolocation')->new();
        
        my $res = $geobase->pinpoint_geolocation($geolocation_search_data, '', '', $geolocation);
        ok(defined $res, 'res defined');
        #косяк. выдача зависит от версии
        if ($libgeobase eq 'geobase4') {
            is($geolocation->region_id, 0, 'default region_id v4 0');
        } elsif ($libgeobase eq 'geobase5') {
            is($geolocation->region_id, 10000, 'default region_id v5 10000');
        } else {
            fail('Unsupported geolib version');
        }
        is($geolocation->precision, 0, 'precision 0');
    };
    
    subtest 'ip yp ys set, gid 123556' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        $geobase->set_new_geolocation_used(1);
        
        my $geolocation_search_data = ($libgeobase . '::geolocation_search_data')->new();
        $geolocation_search_data->set_ip('::ffff:87.10.233.170');
        $geolocation_search_data->set_yandex_gid('123556');
        my $geolocation = ($libgeobase . '::geolocation')->new();
        
        my $res = $geobase->pinpoint_geolocation($geolocation_search_data, '', '', $geolocation);
        ok(defined $res, 'res defined');
        
        my $region = ($libgeobase . '::region')->new;        
        is($geolocation->region_id, 123556, 'region_id 123556');
        $geobase->region_by_id($geolocation->region_id, $region);
        is($region->name, 'Чампино', 'region name Чампино');
        is($geolocation->precision, 2, 'precision 2');
    };
    
    subtest 'ip set, gid incorrect' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        $geobase->set_new_geolocation_used(1);
        
        my $geolocation_search_data = ($libgeobase . '::geolocation_search_data')->new();
        $geolocation_search_data->set_ip('4.58.66.25');
        $geolocation_search_data->set_yandex_gid('999999999999999');
        my $yp = '';
        my $ys = '';
        my $geolocation = ($libgeobase . '::geolocation')->new();
        
        my $res = $geobase->pinpoint_geolocation($geolocation_search_data, '', '', $geolocation);
        ok(defined $res, 'res defined');
        my $region = ($libgeobase . '::region')->new;
        if ($libgeobase eq 'geobase4') {
            is($geolocation->region_id, 84, 'region_id 84');
            $geobase->region_by_id($geolocation->region_id, $region);
            is($region->name, 'США', 'region name США');
        } elsif ($libgeobase eq 'geobase5') {
            is($geolocation->region_id, 87, 'region_id 87');
            $geobase->region_by_id($geolocation->region_id, $region);
            is($region->name, 'Вашингтон', 'region name Вашингтон');
        } else {
            fail('Unsupported geolib version');
        }
        is($geolocation->precision, 4, 'precision 4');
    };
    
    subtest 'ip incorrect, gid set' => sub {
        my $geobase = ($libgeobase . '::lookup')->new($DB_PATH);
        $geobase->set_new_geolocation_used(1);
        
        my $geolocation_search_data = ($libgeobase . '::geolocation_search_data')->new();
        $geolocation_search_data->set_ip('0.58.66.25');
        $geolocation_search_data->set_yandex_gid('123556');
        my $yp = '';
        my $ys = '';
        my $geolocation = ($libgeobase . '::geolocation')->new();
        
        my $res = $geobase->pinpoint_geolocation($geolocation_search_data, '', '', $geolocation);
        ok(defined $res, 'res defined');
        is($geolocation->region_id, 123556, 'region_id 123556');
        
        my $region = ($libgeobase . '::region')->new;
        $geobase->region_by_id($geolocation->region_id, $region);
        is($region->name, 'Чампино', 'region name Чампино');
        is($geolocation->precision, 2, 'precision 2');
    };
};

subtest 'lookup method' => sub {
    #new принимает путь к bin либо путь к конфигу
    subtest 'empty constructor' => sub {
        #пустой new
        eval {
            ($libgeobase . '::lookup')->new();
        };
        ok($@, 'exception');
        like($@, qr/${libgeobase}::lookup::new\(CLASS, geobase_filename\)/, "DIE: ${libgeobase}::lookup::new(CLASS, geobase_filename)");
    };

    subtest 'non existent config' => sub {    
        #несуществующий конфиг
        eval {
            ($libgeobase . '::lookup')->new('/non_existent.conf');
        };
        ok($@, 'exception');
        like($@, qr/config file .+ not found/, 'DIE: config file not found');
    };
    
    # #кривой конфиг
    # косяк. exception не возникает
    # do {
        # my ($fh, $fake_conf_name) = tempfile('/tmp/geobaseXXXXXX', 'SUFFIX' => '.conf', 'UNLINK' => 1);
        # print $fh 'bla bla bla';
        # close $fh;
        # eval {
            # ($libgeobase . '::lookup')->new($fake_conf_name);
        # };
        # unlink $fake_conf_name;
        # ok($@, 'Broken config exception');
        # like($@, qr/verification error, geodata file size is smaller than data format header/, 'verification error, geodata file size is smaller than data format header');
    # };
    
    #конфиг с неправильным путем к БД
    subtest 'wrong config' => sub {
        my ($fh, $fake_conf_name) = tempfile('/tmp/geobaseXXXXXX', 'SUFFIX' => '.conf', 'UNLINK' => 1);
        print $fh 'data_file = /nonexistent_geodata4.bin';
        close $fh;
        eval {
            ($libgeobase . '::lookup')->new($fake_conf_name);
        };
        unlink $fake_conf_name;
        ok($@, 'exception');
        if ($libgeobase eq 'geobase4') {
            like($@, qr/problem with datafile/, 'DIE: problem with datafile');
        } elsif ($libgeobase eq 'geobase5') {
            like($@, qr/problem with initial loading/, 'DIE: problem with initial loading');
        } else {
            fail('Unsupported version');
        }
    };

    #конфиг с неправильным путем к чему-то
    subtest 'wrong config2' => sub {
        my ($fh, $fake_conf_name) = tempfile('/tmp/geobaseXXXXXX', 'SUFFIX' => '.conf', 'UNLINK' => 1);
        print $fh 'data_file = /somedata';
        close $fh;
        eval {
            ($libgeobase . '::lookup')->new($fake_conf_name);
        };
        unlink $fake_conf_name;
        ok($@, 'exception');

        if ($libgeobase eq 'geobase4') {
            like($@, qr/problem with datafile/, 'DIE: problem with datafile');
        } elsif ($libgeobase eq 'geobase5') {
            like($@, qr/problem with initial loading/, 'DIE: problem with initial loading');
        } else {
            fail('Unsupported version');
        }
    };

    #нормальный конфиг
    subtest 'Correct config' => sub {
        my ($fh, $conf_name) = tempfile('/tmp/geobaseXXXXXX', 'SUFFIX' => '.conf', 'UNLINK' => 1);
        print $fh 'data_file = ' . $DB_PATH;
        close $fh;
        eval {
            ($libgeobase . '::lookup')->new($conf_name);
        };
        unlink $conf_name;
        ok(!$@, 'loaded');
    };

    #путь к несущствующей БД
    subtest 'Non existent DB' => sub {
        my $fake_db_path = '/non_existent_db.bin';
        eval {
            ($libgeobase . '::lookup')->new($fake_db_path);
        };
        ok($@, 'exception');
        if ($libgeobase eq 'geobase4') {
            like($@, qr/problem with datafile/, 'DIE: problem with datafile');
        } elsif ($libgeobase eq 'geobase5') {
            like($@, qr/problem with initial loading/, 'DIE: problem with initial loading');
        } else {
            fail('Unsupported version');
        }
    };

    #путь к кривой БД
    subtest 'Broken DB' => sub {
        my ($fh, $db_name) = tempfile('/tmp/geobaseXXXXXX', 'SUFFIX' => '.bin', 'UNLINK' => 1);
        print $fh 'blabla';
        close $fh;
        eval {
            ($libgeobase . '::lookup')->new($db_name);
        };
        unlink $db_name;
        ok($@, 'exception');
        
        like($@, qr/verification error, geodata file size is smaller than data format header/, 'DIE: verification error, geodata file size is smaller than data format header');
    };
    
    #путь к нормальной БД
    subtest 'Correct DB' => sub {
        eval {
            ($libgeobase . '::lookup')->new($DB_PATH);
        };
        ok(!$@, 'loaded');
    };
};
