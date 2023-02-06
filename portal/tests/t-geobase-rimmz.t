#!/usr/bin/perl

use strict;
use warnings;

use lib::abs qw(. ../wadm/tests ../lib ../wbox/lib ../wadm/lib ../wdgt/lib);

use Test::More;
use Data::Dumper;
use Benchmark qw(:all);
use Time::HiRes qw/gettimeofday tv_interval/;

#use InitBase;

#use InitUtils;

use MordaX::Utils;
use MordaX::YCookie;
use Geo;
$Geo::allow_yandex = 1;

use WADM::Utils qw(logit);

our %Region;

my $geobase_file = '/opt/www/bases/geobase.pm';
if ($ARGV[0]) {
    $geobase_file = $ARGV[0];
}

is(Geo::init(), undef, 'init ok');

diag('test depricated');
done_testing();
exit 0;

#ok(-f $geobase_file, 'file found');
#require_ok($geobase_file);
ok(\%geobase::Region, 'Region Inited');

ok(scalar keys %geobase::Region, 'We have some data in Geobase');
#ok(\%Region                ,'Region Exported');
our $geobase = \%geobase::Region;

#ok( Geo::get_geo_code() );
ok(Geo::get_geo_code('127.0.0.1', '192.168.0.1'), 'old search');
#is( Geo::get_geo_code_extended(), undef );
ok(Geo::get_geo_code_by_request({}), 'new search');
#warn Data::Dumper::Dumper( Geo::get_geo_code_core( ip => '96.108.172.116', gid=> undef, yp => undef, ys=>undef ), 'new search 95');
#warn Data::Dumper::Dumper( Geo::get_geo_code_core( ip => '95.108.172.116', gid=> undef, yp => undef, ys=>undef ), 'new search 96');

$MordaX::Errorlog::setuplogging{debug} = 0;

subtest "Test output" => sub {

    my $cx_ok = 0;
    my $cx    = 0;

    open(INTEST, '/opt/www/bases/test/geolocation_test_data');
    while (1) {
        my $in = <INTEST>;
        chomp($in);
        last unless $in;
        my $out = <INTEST>;
        chomp($out);
        <INTEST>;
        my ($yandex_gid, $lat, $lon, $ip, $is_trusted) = split(/\s*,\s*/, $in);

        my $req = build_req(
            gid        => $yandex_gid,
            lat        => $lat,
            lon        => $lon,
            ip         => $ip,
            is_trusted => $is_trusted,
        );

        #warn "Trust: $is_trusted";

        my $result = Geo::get_geo_code_by_request($req);
        is($result->{ok}, 1, 'detection ok');
        my @out = split(',', $out);
        my @out2 = @out;
        #diag('<' . $in );
        #diag('>' . join(', ', @out));
        my $ok = 1;
        for (qw/pure_region precision point_id suspected_region lat lon update_cookie/) {
            my $val = shift @out;
            next if $_ eq 'inc';

            #if( $result->{$_} ){
            $ok = $ok && (($result->{$_} || 0) == $val);
            #cmp_ok(($result->{$_} || 0), '==', $val,, 'req:' . $_);
            #
        }
        my %core_attr;
        for (qw/ip ys yp gid/) {
            $core_attr{$_} = $req->{'XT_' . $_};
        }

        my $result2 = Geo::get_geo_code_core(%core_attr);
        is($result2->{ok}, 1, 'core: detection ok');
        #diag('>' . join(', ', @out2) );
        my $ok2 = 1;
        for (qw/pure_region precision point_id suspected_region lat lon update_cookie/) {
            my $val = shift @out2;
            next if $_ eq 'inc';
            #if( $result2->{$_} ){
            #diag(' expeceted '. $val);
            $ok2 = $ok2 && (($result2->{$_} || 0) == $val);
            #cmp_ok(($result2->{$_} || 0), '==', $val,, 'core:' . $_);
            #}
        }

        $cx++;
        $cx_ok++ if $ok and $ok2;
        last if eof(INTEST);
    }
    close(INTEST);
    my $prc = int($cx_ok / $cx * 100);

    cmp_ok($prc, '>', 0,, " Test on $prc % of $cx records passed");
    done_testing();
};

# ------
# SOME unreal explicit test, searching for segfault
# ------
subtest " Explicit 0 " => sub {
    use geobase5;
    my $data        = geobase5::geolocation_search_data->new();
    my $geolocation = geobase5::geolocation->new();
    my $result      = $Geo::geobase->pinpoint_geolocation($data, '', '', $geolocation);

    is($result,                   1,   "OK");
    is($geolocation->region_id(), 213, "Region");
    done_testing();
};
subtest " Explicit -1 -1  " => sub {
    use geobase5;
    my $data = geobase5::geolocation_search_data->new();
    $data->set_ip(-1);
    #$data->set_yandex_gid('-1');
    my $geolocation = geobase5::geolocation->new();
    my $result = $Geo::geobase->pinpoint_geolocation($data, '', '', $geolocation);

    is($result,                   1,   "OK");
    is($geolocation->region_id(), 213, "Region");
    done_testing();
};
subtest " Explicit '-1'  " => sub {
    use geobase5;
    my $data = geobase5::geolocation_search_data->new();
    $data->set_ip('83.149.3.25');
    $data->set_yandex_gid('-1');
    my $geolocation = geobase5::geolocation->new();
    my $result = $Geo::geobase->pinpoint_geolocation($data, '', '', $geolocation);

    is($result,                   1, "OK");
    is($geolocation->region_id(), 2, "Region");
    done_testing();
};
subtest " Explicit " => sub {
    use geobase5;
    my $data = geobase5::geolocation_search_data->new();
    $data->set_ip('83.149.3.25');
    $data->set_yandex_gid(-1);
    my $geolocation = geobase5::geolocation->new();
    my $result = $Geo::geobase->pinpoint_geolocation($data, '', '', $geolocation);

    is($result,                   1, "OK");
    is($geolocation->region_id(), 2, "Region");
    done_testing();
};

done_testing();
exit();

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

#load lenta
my @lenta;
open(INSTRESS, lib::abs::path('./geolocation_test_data_stress'));
while (<INSTRESS>) {
    chomp();
    my @in = split(',', $_);
    #-1,55.7557680,37.6176710,80.92.96.71,0,100000
    my $req = build_req(
        gid        => $in[0],
        lat        => $in[1],
        lon        => $in[2],
        ip         => $in[3],
        is_trusted => $in[4],
    );
    push @lenta, $req;
    #
    #y $result = Geo::get_geo_code_extended( $req );
}
close(INSTRESS);

ok($#lenta, "lenta loaded");

SKIP: {
    skip "Just Skip Stress test", 1;
    subtest "STRESS TEST" => sub {
        my $count = 0;
        my $i     = 0;
        timethese(
            10_000, {
                'OLD' => sub {
                    my $req = $lenta[$i];
                    Geo::get_geo_code($req->{'RemoteIp'}, $req->{'RemoteIp'});
                    $i++;
                    $i = 0 if ($i > $#lenta);
                },
                'New' => sub {
                    my $req = $lenta[$i];
                    Geo::get_geo_code_extended($req);
                    $i++;
                    $i = 0 if ($i > $#lenta);
                },
                'core' => sub {
                    my $req = $lenta[$i];
                    my %attr;
                    for (qw/ip yp ys gid/) {
                        $attr{$_} = $req->{'XT_' . $_};
                    }
                    Geo::get_geo_code_core(%attr);
                    $i++;
                    $i = 0 if ($i > $#lenta);
                  }
            }
        );
        done_testing();
    };
#END SKIP
}

done_testing();
exit();

#load 2nd lenta
my $time = time;
my @hlenta;
open(INSTRESS, "10k.gpauto");
while (<INSTRESS>) {
    chomp();
    if ($_ =~ m/^([\d\.]+) .* (ys=[\w\.\:\_]+)/) {
        my $ip = $1;
        my $ys = $2;

        unless ($ys =~ /gpauto/) {
            next;
        }
        my $geo = $Geo::geobase->region_id($ip);
        my $path = geo $geo, 'path';
#        warn "> GEO: $geo: ". $path ;
        unless (scalar grep { $_ == 225 } @$path) {
            next;
        }
#        warn "> Add";
        $ys =~ s/:\d+$/:$time/;
        $ys =~ m/gpauto\.([\w\_\:\.]+)/;
        my $gpauto = $1;

        my $req = build_req(
            ip => $ip,
        );
        $req->{XT_gpauto} = $gpauto;
        push @lenta,  $req;
        push @hlenta, $req;
    }

    #
    #y $result = Geo::get_geo_code_extended( $req );
}
close(INSTRESS);
logit('info', "Lenta has: " . (scalar @lenta) . 'records');

# detect

=c1
for(1 .. 5){
    foreach my $req ( @lenta ){
         my %attr;
        for(qw/ip gpauto ygu gid/){
            $attr{$_} = $req->{'XT_'.$_};
        }
        #time THIS
        my $t0 = [gettimeofday];
            Geo::get_geo_code_core( %attr );
        my $elapsed = tv_interval ( $t0, [gettimeofday]);
        $req->{bench_time} += $elapsed;
    }
}
 my $max_time =0;
 my $min_time = 1000;
 foreach( @lenta ){
    if($_->{bench_time} > $max_time){
        $max_time = $_->{bench_time};
    }
    if($_->{bench_time} < $min_time){
        $min_time = $_->{bench_time};
    }
 }

 logit('info', "Max Time: $max_time, $min_time");
 my @heavy_lenta =  grep { $_->{bench_time} > $max_time * 0.9 } @lenta ;
 logit('info', "Heavy lenta has:" . $#heavy_lenta ." resords" );
=cut

=old
my $i =0;
for( 0 .. 1 ){
    my $max = 0;
    my $t0 = [gettimeofday];
    for( 0 .. 2000 ){
        my $req = $hlenta[$i];
        my %attr;
        for(qw/ip gpauto ygu gid/){
            $attr{$_} = $req->{'XT_'.$_};
        }
        my $t0 = [gettimeofday];
        Geo::get_geo_code_core( %attr );
        my $elapsed = tv_interval ( $t0, [gettimeofday]);
        $max = $elapsed if $max < $elapsed;
        $i++;
        $i = 0 if( $i > $#hlenta );
    }
    my $elapsed = tv_interval ( $t0, [gettimeofday]);
    print $elapsed . ";" . $max . "\n";
}

subtest "STRESS TEST heavy" => sub {
    my $count = 0;
    my $i = 0;
    timethese( 100000, {
        'OLD' => sub {
            my $req = $hlenta[$i];
            Geo::get_geo_code( $req->{'RemoteIp'}, $req->{'RemoteIp'} );
            $i++;
            $i = 0 if( $i > $#hlenta );
        },
        'core' => sub {
            my $req = $hlenta[$i];
            my %attr;
            for(qw/ip gpauto ygu gid/){
                $attr{$_} = $req->{'XT_'.$_};
            }
            Geo::get_geo_code_core( %attr );
            $i++;
            $i = 0 if( $i > $#hlenta );
        }
    });
    done_testing();
};
=cut

for my $req (@hlenta) {
#    print $req->{'RemoteIp'} . " - \"ys=gpauto.$req->{XT_gpauto}\"\n";
}
logit('info', "Heavy lenta has:" . $#hlenta . " resords");
# logit('info', "Max Time: $max_time, $min_time");

=c
for( 0 .. 9 ){
    my $prc = $_ * 0.1;
    my $prc_hi = ($_ + 1) * 0.1;
    my $cx = scalar grep { ($_->{bench_time} <= $prc_hi * $max_time ) and ($_->{bench_time} > $prc * $max_time )  } @lenta;
    print STDERR " PRC: $prc  = $cx\n";
} 
=cut

sub build_req {
    my %attr = @_;

    my ($yandex_gid, $lat, $lon, $ip, $is_trusted) = (
        $attr{gid}        || '',
        $attr{lat}        || '',
        $attr{lon}        || '',
        $attr{ip}         || '',
        $attr{is_trusted} || '',
    );

    my $req = {
        'time' => time(),
    };

    my ($ys, $yp) = ('', '');

    if ($ip ne '-1') {
        $req->{'RemoteIp'} = $ip;
        $req->{XT_ip} = $ip;
    }
    $req->{'Cookies'} = {};

    if ($yandex_gid ne '-1') {
        $req->{'Cookies'}->{yandex_gid} = $yandex_gid;
        $yp = (time() + 3000) . '.ygu.' . ($is_trusted ? 0 : 1);

        $req->{XT_gid} = $yandex_gid;
        $req->{XT_ygu} = ($is_trusted ? 0 : 1);
    }

    $lat =~ tr/\./_/;
    $lon =~ tr/\./_/;
    if ($lat ne '-1') {
        my $gpauto = join(':', $lat, $lon, 150, 1, time() - 1800);
        $ys = 'gpauto.' . $gpauto;    #55_734149:37_587933:150:1:1259758354

        $req->{XT_gpauto} = $gpauto;
    }
    my $ycookie = MordaX::YCookie->new(
        $req,
        ys => $ys,
        yp => $yp,
    );

    # print
    $req->{YCookie}           = $ycookie;
    $req->{XT_ys}             = $ys;
    $req->{XT_yp}             = $yp;
    $req->{'Cookies'}->{'yp'} = $yp;
    $req->{'Cookies'}->{'ys'} = $ys;

    return $req;
}

#benchmark

