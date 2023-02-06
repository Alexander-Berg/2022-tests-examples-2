#!/usr/bin/perl

use Test::More;
use common::sense;
use lib::abs qw(../lib ../scripts);

#use InitBase;
#use InitUtils;
use MP::Utils qw(is_hash is_array);
use MP::Time;
use MordaX::Logit qw(logit dmp);
use Geo;
use MordaX::Cache;

require_ok('export_hockey2015.pl');
use_ok("MordaX::Block::Hockey2015");
use MordaX::Block::Hockey2015;

my $data_file = lib::abs::path("./data/hockey2015-memd.json");

is(Geo::geo(213, 'timezone'), "Europe/Moscow");
ok(geo(213, 'name'), "Moscow has name");
my $memd = MordaX::Cache->new();
ok($memd);
my $hmem = $memd->get('hockey');

if ($hmem) {
    test_mem_struct($hmem);
}

diag("sw ./scripts/export_hockey2015.pl -d -u -l --date-shift=2015-05-01");
diag("./tools/get_memd_data hockey > $data_file");

my $mock = MP::Utils::parse_json_file($data_file);
ok($mock);
ok($mock->{blocks}, "Mock file $data_file has blocks");
test_mem_struct($mock);

$mock->{blocks} = [grep { $_->{block_key} ne '2015-05-04' } @{$mock->{blocks}}];

subtest "Block Selection" => sub {

    is(t_select_block($mock, "2015-04-25T11:09", 213)->{block_key}, "2015-05-01", "To young");
    #my $b1 = t_select_block( $mock, "2015-04-27T10:59", "Europe/Moscow");
    #dmp( $b1 );
    #is( $b1->{block_key}, "2015-05-01" );

    is(t_select_block($mock, "2015-04-27T10:09", 213)->{block_key}, "2015-05-01");
    is(t_select_block($mock, "2015-04-27T11:09", 213)->{block_key}, "2015-05-01");
    is(t_select_block($mock, "2015-04-28T10:59", 213)->{block_key}, "2015-05-01");
    is(t_select_block($mock, "2015-04-28T11:09", 213)->{block_key}, "2015-05-02");
    is(t_select_block($mock, "2015-04-29T11:09", 213)->{block_key}, "2015-05-03");
    #05-04 skipped
    is(t_select_block($mock, "2015-04-30T10:59", 213)->{block_key}, "2015-05-03");
    is(t_select_block($mock, "2015-04-30T12:09", 213)->{block_key}, "2015-05-03");
    #NEXT DAY
    diag("next block");
    is(t_select_block($mock, "2015-04-30T12:16", 213)->{block_key}, "2015-05-05");

    #kaliningrad
    is(t_select_block($mock, "2015-04-25T11:09", 22)->{block_key}, "2015-05-01", "To young");
    is(t_select_block($mock, "2015-04-27T10:09", 22)->{block_key}, "2015-05-01");
    is(t_select_block($mock, "2015-04-27T11:09", 22)->{block_key}, "2015-05-01");

    is(t_select_block($mock, "2015-04-28T10:10", 22)->{block_key}, "2015-05-01");
    #10:59 Kaliningrad is 11:59 msk, but block start in announce mode in 11:15msk( 2 hours from game 13:15msk)
    is(t_select_block($mock, "2015-04-28T10:59", 22)->{block_key}, "2015-05-02");
    is(t_select_block($mock, "2015-04-28T11:09", 22)->{block_key}, "2015-05-02");

    #TAIL
    is(t_select_block($mock, "2015-04-29T10:10", 22)->{block_key}, "2015-05-02");
    #ACTIVE
    is(t_select_block($mock, "2015-04-29T10:16", 22)->{block_key}, "2015-05-03");
    is(t_select_block($mock, "2015-04-29T11:09", 22)->{block_key}, "2015-05-03");

    #05-04 skipped
    is(t_select_block($mock, "2015-04-30T01:59", 22)->{block_key}, "2015-05-03");
    #is(  t_select_block( $mock, "2015-04-30T03:59", 22 )->{block_key}, "2015-05-03");
    #is(  t_select_block( $mock, "2015-04-30T08:59", 22 )->{block_key}, "2015-05-03");
    #is(  t_select_block( $mock, "2015-04-30T10:59", 22 )->{block_key}, "2015-05-03");
    is(t_select_block($mock, "2015-04-30T11:09", 22)->{block_key}, "2015-05-03");
    #TAIL 15 hour end
    is(t_select_block($mock, "2015-04-30T11:16", 22)->{block_key}, "2015-05-05");
    is(t_select_block($mock, "2015-04-30T12:09", 22)->{block_key}, "2015-05-05");

    #last one
    is(t_select_block($mock, "2015-05-30T12:09", 22)->{block_key}, "2015-05-05");

    done_testing();
};

done_testing();

our $mmm;

sub t_select_block {
    my ($mem, $tt, $geo) = @_;

    unless ($tt =~ m/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/) {
        fail("Not valid TTime: $tt");
        return;
    }
    if ((!$mem->{blocks}) || !(scalar @{$mem->{blocks}})) {
        fail("no Blocks");
        return;
    }
    my $tz = Geo::geo($geo, 'timezone');
    #dmp( $mem->{blocks} );
    my %ltime;

    @ltime{qw/year mon  mday hour min sec/} = ($1, $2, $3, $4, $5, 1);
    my $ts = MP::Time::ltime_to_ts(\%ltime, $tz);
    diag($tt, "+", $tz, "=", $ts);
    my $req = {
        'time'          => $ts,
        'timezone'      => $tz || 'Europe/Moscow',
        'GeoByDomainIp' => $geo,
    };
    MordaX::Input::init_geoinfo(undef, $req);
    my $b = MordaX::Block::Hockey2015::select_block($req, $mem->{blocks});
    return $b;
}

sub test_mem_struct {
    $mmm = shift;
    subtest "MEMORY CHECK" => sub {
        my $blocks = $mmm->{blocks};
        my $tt     = $mmm->{tournament_table};

        ok(is_hash($tt),       "TTable has data");
        ok($tt->{ru},          "Ru has tournament record");
        ok($tt->{ru}->{group}, "Ru has group");
        ok($tt->{ru}->{place}, "Ru has place");

        ok(is_array($blocks), "Found blocks " . scalar @$blocks);

        if (scalar @$blocks) {
            ok($blocks->[0]->{block_key}, "Block key");
            for (my $i = 1; $i < @$blocks; $i++) {
                my $b  = $blocks->[$i];
                my $bp = $blocks->[$i - 1];

                ok($b->{last_ts},                                "last game");
                ok($b->{first_ts},                               "first game");
                ok($b->{last_ts} > $b->{first_ts},               "last more than first");
                ok($b->{block_start_ts},                         "start");
                ok($b->{block_end_ts},                           "end");
                ok($b->{block_start_ts} < $b->{block_end_ts},    "$i : start > end");
                ok($b->{block_start_ts} > $bp->{block_start_ts}, "$i : start > start");
                ok($b->{block_end_ts} > $bp->{block_end_ts},     "$i : start > start");
                ok(scalar @{$b->{events}},                       "HAVE Events");
            }
        }

        done_testing();
      }
}

