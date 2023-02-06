#!/usr/bin/perl

use 5.010;

use Test::More;
use common::sense;
use lib::abs qw(. ../lib ../t/testlib);

#use InitMorda;

use MordaX;

use MordaTest;
use testlib::TestRequest qw(r);
use testlib::GeoHelper;
use MordaX::Cache;
use MP::Utils;

use MordaX::Output;
{
    no warnings;
    sub MordaX::Output::report { 1; }
    use warnings;
}

my $geo = testlib::GeoHelper->new();

my $pid = $$;
ok($pid, "pid ok");
my $mem = get_memory_size();
ok($mem, "initial size: $mem");

done_testing();
exit 0;

subtest "TOUCH MORDA in Spb" => sub {
    my ($req, $input, $r) = r(
        ip      => $geo->ip(2),
        cookies => {
            yandexuid => '812551691384428259',
        },
        headers => {
            'User-Agent' => 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_2_1 like Mac OS X; ru-ru) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20',
        },
    );
    test_memory($r);
    done_testing();

};
#exit();

subtest "BIGMORDA Moscow plain" => sub {
    my ($req, $input, $r) = r(
        ip      => $geo->ip(225),
        cookies => {
            yandexuid => '812551691384428259',
        },
        headers => {
            'User-Agent' => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0'
        },
    );
    test_memory($r);
    done_testing;
};
subtest "BIGMORDA Moscow Widget" => sub {
    my ($req, $input, $r) = r(
        ip      => $geo->ip(225),
        cookies => {
            yandexuid => '812551691384428259',
            w         => '1..d6pule..1385400635930600..._l4jRcA.14064337.1406.bca5e65ddc2b13ad4efe6e8d1e6fc9e5',
        },
        headers => {
            'User-Agent' => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0'
        },
    );
    test_memory($r);
    done_testing;
};
done_testing();

sub test_memory {
    my $r = shift;
    #local *STDOUT;
    #local *STDERR;
    my $std = save_handle(\*STDOUT);
    my $err = save_handle(\*STDERR);

    test_memory_by_condition('full', $r, 2, 0);    #0 for tmpl test (js is leaking )

    local *MordaX::Draw = sub { return ("", "", ""); };
    test_memory_by_condition('no-tmpl', $r, 100, 0.3);

    restore_handle(\*STDOUT, $std);
    restore_handle(\*STDERR, $err);
    #ok( $ok >= $ok_condition, "$ok_condition trys with non changed mem, after " . $cx . " tries");
}

sub test_memory_by_condition {
    my ($type, $r, $max, $threshold) = @_;
    $type      //= 'common';
    $max       //= 200;
    $threshold //= 0.1;

    my $ok_condition = int($max * $threshold);
    my $s            = [get_memory_size()];
    my $ok           = 0;
    my $max_ok       = 0;
    for (1 .. $max) {
        MordaX::handler(
            MP::Utils::xclone($r)
        );
        MordaX::Cache->cleanup();
        push(@$s, get_memory_size());
        if ($s->[-1] == $s->[-2]) {
            $ok++;
        } else {
            $max_ok = $ok if $max_ok < $ok;
            $ok = 0;
        }
        if ($ok >= $ok_condition) {
            #last;
        }
    }

    $max_ok = $ok if $max_ok < $ok;
    my $cx = scalar(@$s) - 1;

    ok($max_ok >= $ok_condition);
    diag("  [$type] $max_ok trys with non changed mem, after " . $cx . " tries");
    diag("  [$type] Memory leak: " . ($s->[-1] - $s->[0]) . "k Average " . ($s->[-1] - $s->[0]) / ($cx + 1) . "k/req");

    #diag( join(', ', @$s) );

    return $max_ok >= $ok_condition ? 1 : 0;
}

sub get_memory_size {
    my $pid = shift || $$;
    my @l = split(/[\n\r]+/, `ps ux`);
    for (@l) {
        my @v   = split(/\s+/, $_);
        my $p   = $v[1];
        my $vss = $v[4];
        my $rss = $v[5];
        return $vss + $rss if $p == $pid;
    }
}

sub save_handle {
    my $stream = shift;
    my $buff = shift || '';

    open(my $std, '>&', $stream);
    close(*$stream);
    open(*$stream, '>', \$buff);

    return $std;
}

sub restore_handle {
    my ($stream, $copy) = @_;
    close(*$stream);
    open(*$stream, '>&', *$copy);
}
