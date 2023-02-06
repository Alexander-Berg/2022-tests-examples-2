#!/usr/bin/perl

use common::sense;
use lib::abs qw( ../lib ../t/testlib . );
use Test::More;
use Storable;
use MordaTest;
use testlib::TestRequest qw/r/;
use MordaX::Logit qw/dmp/;
use MordaX::Cache;

#use utf8;

use_ok('MordaX::Block::Tv');

my $memd = MordaX::Cache->new();
my $r    = r();
my $sample;    #see sample in bottom of file
ok($r);
ok($memd, "MEMD");
is(ref($memd), 'MordaX::CacheFaker', 'CacheFaker online');

my $tv = MordaX::Block::Tv->new();

my $page = {};
#my $tv_call = $tv->GetData( $r , $page );
#dmp( $page );

#subtest "A1:Test Announces" => sub {
#    ok( $page->{TV}->{announces} , "Announces presents");
#    done_testing();
#};
subtest "A2, test ending time" => sub {
    my $r = r('time' => $sample->{A2}->{time});
    $memd->set_mock(%{$sample->{A2}->{memd}});

    #dmp( $memd->s() );

    my $page      = {};
    my $tv_call   = $tv->GetData($r, $page);
    my $is_hol_hr = Holidays::holidays_ytt($r);
    is($r->{time},                $sample->{A2}->{time}, "time ok");
    is($is_hol_hr->{'yesterday'}, undef,                 "Yesterday not holiday");
    is($is_hol_hr->{'today'},     undef,                 "Today not holiday");
    is($is_hol_hr->{'tomorrow'},  undef,                 "Tomorrow not holiday");
    ok($page);
    ok($page->{TV});
    my $tv = $page->{TV};
    is($tv->{evening_mode}, 0, "7:40 isnt evening");
    is($tv->{weekend_mode}, 0, "thusday no week end");

    #dmp( $page->{TV} );
    ok($tv->{programms}, "Programs");
    is(@{$tv->{programms}}, 1, "one programm left");
    #dmp( $tv->{programms} );
    like($tv->{programms}->[0]->{ch_href}, qr/162$/, "last program from 353 channel");
    done_testing();
};

subtest "A3" => sub {
    my $r = r('time' => $sample->{A3}->{time});
    $memd->set_mock(%{$sample->{A3}->{memd}});
    my $page = {};
    my $tv_call = $tv->GetData($r, $page);

    is($r->{time}, $sample->{A3}->{time}, "time ok");
    my $p = $page->{TV};

    is($p->{evening_mode}, 1, "19:30 is evening");
    is($p->{weekend_mode}, 0, "thusday - no week end");

    #dmp( $page->{TV} );
    ok($p->{programms}, "Programs");
    is(@{$p->{programms}}, 1, "one programm left");
    #is( $p->{programms}->[-1]->{ch_id}, 353, "last program from 353 channel");

    done_testing();
};
subtest "A3 announce events" => sub {

    my $r = r('time' => $sample->{A3}->{time});
    my $mock = Storable::dclone($sample->{A3}->{memd});
    for my $ch (keys %$mock) {
        for (@{$mock->{$ch}}) {
            #dmp( $ch, $_ );
            $_->{type} = 4;
        }
    }
    $memd->set_mock(%{$mock});
    my $page = {};
    my $tv_call = $tv->GetData($r, $page);

    my $p = $page->{TV};
    ok($p->{programms}, "Programs");
    is(@{$p->{programms}}, 1, "one programm left");
    #is( $p->{programms}->[-1]->{ch_id}, 353, "last program from 353 channel");
    done_testing();
};

subtest "P1 profiling" => sub {
    $memd->clean();
    bless($memd, "MordaX::Cache");
    for (my $i = 0; $i < 3000; $i++) {
        my $page = {};
        #    my $tv = MordaX::Block::Tv->new();
        #my $tv_call = $tv->GetData( $r , $page );
        #$memd->cleanup();
    }
    ok(1, "Profiling finished");
    done_testing();
};

done_testing();

BEGIN {
    $sample = {
        "A2" => {

            'time' => 1382414000,    #вторник 7:53
            'memd' => {
                "tv_schedule_kubr_146" => [
                    {
                        "channel"  => 146,
                        "chf"      => 16,
                        "start_s"  => 1382414000 + 60 + 600 - 3600,
                        "duration" => 3600,
                        "end_s" => 1382414000 + 60 + 600, #окончание передачи через 11 минут, по новой логике отсекаем
                        "eventid"  => 46263439,
                        "id"       => 2125,
                        "programm" => 2125,
                        "subtitle" => undef,
                        "title"    => "Давай поженимся!",
                        "type"     => 6
                    },
                ],
                "tv_schedule_kubr_162" => [
                    {
                        "channel"  => 162,
                        "chf"      => 11,
                        "programm" => 7030,
                        "start_s"  => 1382414000 + 61 + 480 - 1800,
                        "duration" => 1800,
                        "end_s" => 1382414000 + 61 + 480, #окончание передачи через 9 минут по старой и новой логике - отключаем
                        "eventid"  => 46263948,
                        "id"       => 7030,
                        "subtitle" => undef,
                        "title"    => "Сегодня.",
                        "type"     => 2
                    },
                    {
                        "channel"  => 162,
                        "chf"      => 11,
                        "programm" => 7036,
                        "start_s"  => 1382414000 + 61 + 480 - 1800,    #
                        "duration" => 3600,
                        "end_s" => 1382414000 + 61 + 480 - 1800 + 3600, #окончание передачи через 9 минут новой логике - отключаем
                        "eventid"  => 46263948,
                        "id"       => 7036,
                        "subtitle" => undef,
                        "title"    => "Сегодня. 9m - 2",
                        "type"     => 2
                    },

                ],
                "tv_schedule_kubr_353" => [
                    {
                        "channel"  => 353,
                        "chf"      => 33,
                        "start_s"  => 1382414000 + 62 + 1200 - 3600,
                        "duration" => 1800 + 3600,
                        "end_s"    => 1382414000 + 62 + 1200,          #окончание через 21минут - оставляем
                        "eventid"  => 46270078,
                        "id"       => 268165,
                        "programm" => 2413,
                        "subtitle" => "138-я серия.",
                        "title"    => "Интерны.",               #announced
                        "type"     => 6
                    },
                ],
                "tv_schedule_kubr_711" => [],
                "tv_schedule_kubr_79"  => [],
              }
        },    #END of A2
        A3 => {
            'time' => 1382460000,    #20:40
            'memd' => {
                "tv_schedule_kubr_146" => [
                    {
                        "channel"  => 146,
                        "chf"      => 16,
                        "start_s"  => 1382460000 + 60 + 600 - 3600,    #19 52
                        "duration" => 3600,
                        "end_s" => 1382460000 + 60 + 600, #окончание передачи через 11 минут, по новой логике отсекаем #20:52
                        "eventid"  => 46263439,
                        "id"       => 2125,
                        "programm" => 2125,
                        "subtitle" => undef,
                        "title"    => "Давай поженимся! 11m less then 12",
                        "type"     => 6
                    },
                ],
                "tv_schedule_kubr_162" => [
                    {
                        "channel"  => 162,
                        "chf"      => 11,
                        "programm" => 7030,
                        "start_s"  => 1382460000 + 61 + 480 - 1800,    #
                        "duration" => 1800,
                        "end_s" => 1382460000 + 61 + 480, #окончание передачи через 9 минут новой логике - отключаем
                        "eventid"  => 46263948,
                        "id"       => 7030,
                        "subtitle" => undef,
                        "title"    => "Сегодня. 9m",
                        "type"     => 2
                    },

                ],
                "tv_schedule_kubr_353" => [
                    {
                        "channel"  => 353,
                        "chf"      => 33,
                        "start_s"  => 1382460000 + 62 - 1800,
                        "duration" => 1800 + 3600,
                        "end_s"    => 1382460000 + 62 + 3600,            #окончание через 21минут - оставляем
                        "eventid"  => 46270078,
                        "id"       => 268165,
                        "programm" => 2413,
                        "subtitle" => "138-я серия. 21min left",
                        "title"    => "Интерны. 21min",
                        "type"     => 4
                    },
                ],
                "tv_schedule_kubr_711" => [],
                "tv_schedule_kubr_79"  => [],
              }
        },    #END of A3

      }    #END of sample HASH
}    #END of BEGIN
