package testlib::GeoHelper;
use rules;
use JSON::XS;
use lib::abs;
use Geo;

use lib::abs qw(../../lib);
use MP::Logit qw(dmp logit);

my $region_ip        = {};
my $tested_region_ip = {};
my $object;

my $path_to_file = lib::abs::path(qw{../../t/bases/ip_base.json});

sub new {
    return $object if $object;

    $object = {};
    bless($object, 'testlib::GeoHelper');
    $object->init();

    return $object;

}

sub init {
    my $this = shift;

    my $ip_base = $this->data_file();
    if (!-f $ip_base) {
        $region_ip = {};
        return 1;
    }
    my $in;
    open($in, $ip_base) or die("cannot open $ip_base ");
    local $/ = undef;
    my $data = <$in>;
    $region_ip = JSON::XS->new()->decode($data) || {};
    close($in);

    #dmp('load 159', $region_ip->{159} );
    return 1;
}

sub save {
    my $this = shift;

    #dmp("Save 159", $region_ip->{159} );
    my $ip_base = $this->data_file();
    my $out;
    if( open($out, ">", $ip_base) ){
        print $out JSON::XS->new->pretty(1)->canonical(1)->encode($region_ip);
        close($out);
    }
    1;
}

sub ip {
    my ($this, $region) = @_;
    return get_region_ip($region);
}

sub get_region_ip {
    my $region = shift;
    my $ips    = clean_up_region($region);

    #dmp( "Region", $region, "IPS:", $ips);

    if ($ips) {
        return $ips->[rand scalar @$ips];
    }

    my $ip = ipv4_scan_for_region($region);
    unless ($ip) {
        warn "IP for region $region not found in one scan";
    }
    return $ip;
}

sub all_ips {
    my $ips = [];
    for my $ip (values %$region_ip) {
        eval {
            push @$ips, @$ip;
        };
        if ($@) {
            push @$ips, $ip;
        }
    }
    $ips;
    #dmp($ips);
}

sub region_by_ip {
    my ($this, $ip) = @_;
    my $decode = Geo::get_geo_code_core(ip => $ip);
    if ($decode->{precision} > 0) {
        return $decode->{pure_region_by_ip};    #|| $decode->{region_id}
    }
    undef;
}

sub ipv4_scan_for_region {
    my $region = shift;

    local $Geo::laas = 0;
    for (my $cx = 0; $cx < 100000; $cx++) {
        my @ip_p = ();
        for (1 .. 4) {
            push @ip_p, int(rand(253) + 1);
        }
        my $ip_str = join('.', @ip_p);

        my $r = region_by_ip(undef, $ip_str);
        next unless $r;

        #clean_up_region( $r );
        add_ip_to_region($ip_str, $r);

        if ($r == $region) {
            return $ip_str;
        }
    }
}

sub clean_up_region {
    my $r = shift;
    if (!$tested_region_ip->{$r}) {
        my $ips = $region_ip->{$r};
        if (ref($ips) ne 'ARRAY') {
            $ips = [$ips];
        }

        my @ok;

        #dmp( "Region for Disk DB", $ips ) if $r == 159;
        for my $ip (@$ips) {
            my $new_r = region_by_ip(undef, $ip);
            #dmp( "IP" , $ip, "REgion:", $new_r, "Expected: ", $r ) if $r == {159} ;
            if ($r == $new_r) {
                push @ok, $ip;
            }
        }

        if (scalar @ok == 0) {
            delete $region_ip->{$r};
        } else {
            # SORT!! not to modify t/bases/ip_base.json
            $region_ip->{$r} = [sort @ok];
        }

        #dmp("Filterd", $region_ip->{$r} );
        #logit('debug', "Region $r Readed from disk:" , scalar @{ $region_ip->{$r} } );

        $tested_region_ip->{$r} = 1;
    }
    return $region_ip->{$r};
}

sub add_ip_to_region {
    my ($ip, $region) = @_;
    my $ips = $region_ip->{$region};

    if (ref($ips) eq 'ARRAY') {
        if (scalar @$ips >= 10) {
            #splice( @$ips, rand(10), scalar( @$ips ) - 9  );
        } else {
            push @$ips, $ip;
        }
    }
    else {
        $region_ip->{$region} = [$ip];
    }
    return $region_ip->{$region};
}

sub data_file {
    $path_to_file
      #lib::abs::path( qw{./bases/ip_base.json} );
}

sub DESTROY {
    my $this = shift;
    $this->save();
}
1;
