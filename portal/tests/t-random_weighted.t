#!/usr/bin/perl
use common::sense; use warnings "NONFATAL" => "all"; no warnings qw(uninitialized);    #common v2
#use Test::Most;
use Test::More;
use 5.010;
use lib::abs qw(../lib .);
use Data::Dumper;
use MP::Logit qw(dmp);
use_ok("MordaX::Utils");

*randw = *MordaX::Utils::random_weighted;

subtest "Zerro input weight" => sub {
    my $hashdata = {
        some => {
            v      => 'some',
            weight => 1,
        },
    };
    my $zerrodata0 = [];
    my $zerrodata  = [
        {id => 1, weight => 0,},
        {id => 2, weight => 0,},
        {id => 3, weight => 0,},
    ];
    my @emptyAnswer = randw($zerrodata0);
    is($#emptyAnswer, -1, 'no input no output');

    my @emptyAnswerOnHash = randw($hashdata);
    is($#emptyAnswerOnHash, -1, 'no input array no output');

    my @emptyAnswerZerro = randw($zerrodata);
    is($#emptyAnswerZerro, -1, 'Zerro Weight input, no output');
    done_testing();
};

sub deviation {
    my ($get, $expect) = @_;
    return abs($get - $expect) * 2 * 100 / (abs($get) + abs($expect));
}
subtest "Default weight" => sub {
    my $input = [
        {id => 1, weight => 0},
        {id => 2, weight => ''},
        {id => 3, weight => undef},
        {id => 4, weight => 1},
    ];

    #max item return;
    my @zerro = randw($input, {max => 0});
    my @one   = randw($input,);
    my @three = randw($input, {max => 3});
    my @four  = randw($input, {max => 4});

    is($#zerro, -1, "Zerro max");
    is($#one,   0,  'default max');
    is($#three, 2,  '3 is 3');
    is($#four,  2,  '4 but still 3 ');

    #probamility
    my $sum   = {};
    my $max   = 2;
    my $count = 3000;
    for (1 .. $count) {
        my @any = randw($input, {max => $max});
        for (@any) {
            $sum->{$_->{id}}++;
        }
    }

    my $expect = $count * $max / 3;
    is($sum->{1}, undef, 'Zerro weighted not selected');
    for (2 .. 4) {
        ok(deviation($sum->{$_}, $expect) < 10, " ID: $_, count: $sum->{$_}, expect => $expect ");

    }
    done_testing();
};

subtest "Mixed Weight" => sub {
    my $input = [
        {id => 1, weight => 0},
        {id => 2, weight => 0, 'bk_tag' => 'x'},
        {id => 3, weight => '', bk_tag => 'x'},
        {id => 4, weight => 1, 'bk_tag' => 'y'},
    ];

    my $max   = 1;
    my $count = 900;
    my $sum   = {};

    for (1 .. $count) {
        my @any = randw($input, {max => $max, bk_tag => 'x', bk_add => 1});
        for (@any) {
            $sum->{$_->{id}}++;
        }
    }

    is($sum->{1}, undef, 'Zerro weighted not selected');

    is($sum->{2}, undef, 'Zerro weighted not selected, no BK_ADD');

    my $expect = $count * $max / 3;

    ok(deviation($sum->{3}, 2 * $expect) < 10, "ID: 2, count: $sum->{3}, expect => 2 * $expect ");

    for (4) {
        ok(deviation($sum->{$_}, $expect) < 10, "ID: $_, count: $sum->{$_}, expect => $expect ");
        note('Deviation:', deviation($sum->{$_}, $expect));
    }

    done_testing();
};

subtest "Other Names for wight field, bk_tag field, DEfault Weight 5" => sub {

    my $input = [
        {id => 1, weight => 0, w => 5},
        {id => 2, weight => 0, w => 5, 'bk' => 'z', 'bk_tag' => 'x'},    #default bk_add is 5 so summary weight will be 10
        {id => 3, weight => '', w => 0, 'bk_tag' => 'x'},
        {id => 4, weight => 1,  w => 0, 'bk_tag' => 'y'},
    ];

    my $count = 3000;
    my $sum   = {};
    for (1 .. $count) {
        my @any = randw($input, {key => 'w', bk_tag => 'z', bk_tag_key => 'bk'});
        for (@any) { $sum->{$_->{id}}++ }
    }
    #dmp( $sum );

    is($sum->{3}, undef, 'Zerro weighted not selected(w)');
    is($sum->{4}, undef, 'Zerro weighted not selected(w)');

    ok(deviation($sum->{1}, $count / 3) < 10,     "ID: 1, count: $sum->{1}, expect => 1000 ");
    ok(deviation($sum->{2}, 2 * $count / 3) < 10, "ID: 2, count: $sum->{2}, expect => 2000 ");

    done_testing();
};

subtest "Less Than Zerro" => sub {
    my $input = [
        {id => 1, weight => -1},
        {id => 2, weight => 1}
    ];

    my $out = randw($input);
    is($out->{id}, 2, "Zeero is ignored");

    $input = [
        {id => 1, weight => 1},
        {id => 2, weight => -0.5},
        {id => 3, weight => 1},
    ];
    my $count = 1000;
    my $sum   = {};
    for (1 .. $count) {
        my @any = randw($input,);
        for (@any) { $sum->{$_->{id}}++ }
    }

    is($sum->{2}, undef, "No LessZerro output");
    ok(deviation($sum->{1}, $count / 2) < 20, "ID: 1, count: $sum->{1}");
    ok(deviation($sum->{3}, $count / 2) < 20, "ID: 3, count: $sum->{3}");

    $input = [
        {id => 1, weight => -1},
        {id => 2, weight => -0.5},
        {id => 3, weight => -10000000},
    ];
    my @emptyAnswer = randw($input);
    is($#emptyAnswer, -1, 'no output for all LessZero weights');

    done_testing();
};

my $blockdata = [];

for (1 .. 10) {
    push @$blockdata, {v => $_, weight => 0};
}

#print Dumper $blockdata;

ok !MordaX::Utils::random_weighted($blockdata, {max => 0}), 'no data 1';
ok !MordaX::Utils::random_weighted($blockdata, {max => 3}), 'no data 3';
ok !MordaX::Utils::random_weighted($blockdata, {max => 5}), 'no data 5';

push @$blockdata, {v => 't', weight => 1};
ok 1 + (@_ = MordaX::Utils::random_weighted($blockdata, {max => 3})), '1 data 3 = ' . scalar @_;
push @$blockdata, {v => 't', weight => 2};
ok 1 + (@_ = MordaX::Utils::random_weighted($blockdata, {max => 3})), '2 data 3 = ' . scalar @_;
push @$blockdata, {v => 't', weight => 3};
ok 1 + (@_ = MordaX::Utils::random_weighted($blockdata, {max => 3})), '3 data 3 = ' . scalar @_;

#print Dumper $blockdata;

$blockdata = [];
for (1 .. 10) {
    push @$blockdata, {v => $_, weight => 0};
}

ok !MordaX::Utils::random_weighted($blockdata, {max => 0}), 'all weight=0 max=0';
ok !MordaX::Utils::random_weighted($blockdata, {max => 1}), 'all weight=0 max=1';
ok !MordaX::Utils::random_weighted($blockdata, {max => 3}), 'all weight=0 max=3';
ok !MordaX::Utils::random_weighted($blockdata, {max => 5}), 'all weight=0 max=5';

$blockdata = [];
for (1 .. 10) {
    push @$blockdata, {v => $_, weight => $_};
}

ok 0 == +(@_ = MordaX::Utils::random_weighted($blockdata, {max => 0})), 'max=0 = ' . scalar @_;
ok + (@_ = MordaX::Utils::random_weighted($blockdata, {max => 1})), 'max=1 = ' . scalar @_;
ok 3 == +(@_ = MordaX::Utils::random_weighted($blockdata, {max => 3})), 'max=3 = ' . scalar @_;
ok 5 == +(@_ = MordaX::Utils::random_weighted($blockdata, {max => 5})), 'max=5 = ' . scalar @_;

#use_ok("MordaX::Block::Services");

=pod
my $blockdata = [];
for (1 .. 1000) {
    my $weight = ($_ % 10 == 0) ? 50 : 1;
    push @$blockdata, { v => $_, weight => $weight };
}
#print Dumper $blockdata;
my $i = 1000;
my $max = 3;
{
    my $freq = {};
    for (1..$i) {
        my @res = MordaX::Utils::random_weighted_old($blockdata, $max);
        for my $e (@res) {
            $freq->{ $e->{v} }++;
        }
    }
    my @freq = ();
    for my $n (sort keys %$freq) {
        push @freq, sprintf ("%.2f",$freq->{$n}/$i);
    }
    note explain \@freq;
}

{
    my $freq = {};
    for (1..$i) {
        my @res = MordaX::Utils::random_weighted($blockdata, $max);
        for my $e (@res) {
            $freq->{ $e->{v} }++;
        }
    }
    my @freq = ();
    for my $n (sort keys %$freq) {
        push @freq, sprintf ("%.2f",$freq->{$n}/$i);
    }
    note explain \@freq;
}

use Benchmark qw(:all);

$max = 20;

cmpthese(-3, {
    'old' => sub {
        my @res = MordaX::Utils::random_weighted_old($blockdata, $max);
    },
    'new' => sub {
        my @res = MordaX::Utils::random_weighted($blockdata, $max);
    },
}, 'all');
=cut

done_testing();
