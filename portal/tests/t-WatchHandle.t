#!/usr/bin/perl

use common::sense;
use lib::abs qw(../lib );
use Test::More;

use strict;
use warnings;

diag('testing file descriptors');

subtest "CLEAN STDERR" => sub {
    diag('Type' . *STDERR);
    my $fn = fileno(STDERR);
    ok($fn, 'Fno: ' . $fn);
    diag('STDIN:' . fileno(STDIN));
    diag('STDOUT:' . fileno(STDOUT));

    done_testing();
};

subtest "BACK UP to Variable" => sub {
    my $backup;
    open($backup, '>&', STDERR);

    is(fileno(STDERR), 2, 'STDERR is stil 2');
    #is( fileno( $backup ),      2, 'Backup is stil 2');

    close(STDERR);
    my $buff = "x";
    open(STDERR, '>', \$buff);
    print STDERR 'example';
    is($buff, 'example', "varible flushed on start, and works");

    is(fileno(STDERR), -1, 'STDERR is -1 for in memory');

    close(STDERR);
    open(STDERR, '>&', \$backup);    #& still opened handler
    print STDERR "#err output\n";

    is(fileno(STDERR), 2, 'STDERR is stil 2');
    #is( fileno( $backup ),      2, 'Backup is stil 2');

    done_testing();
};

=x double route dont work here
subtest "DOUBLE ROUTE" => sub {
    use Symbol;
    my $h1 = Symbol::gensym;
    my $h2 = Symbol::gensym;

    my $h3 = Symbol::gensym;
    my $buff = "";
    open ( $h1, '>', \$buff);
    print $h1 'Hi';
    is($buff, 'Hi', 'first round');

    ok( open( $h2, '>&=', $h1) );
    print $h2 ' man';
    is($buff, 'Hi man', 'second round as alias');
    ok( open( $h3, '>&', $h1) );
    flush( $h1 );
    flush( $h3 );

    print $h3 ' and';

    is($buff, 'Hi man and', 'second round as dup');
    is(fileno($h1), fileno($h2));
    ok(fileno($h3), 'f3:' . fileno( $h3) );
    done_testing(); 
};
=cut

subtest "TIedHadndler TO Var" => sub {
    my $h = \do { local *TIED_TO_VAR };
    is(ref($h), 'GLOB', 'Glob REF: ' . $h);

    use_ok('MordaX::WatchHandle');
    my $cont;
    ok(tie(*$h, 'MordaX::WatchHandle', \$cont), 'Tied To container ' . \$cont);

    is($cont, undef, 'Empty if undefined on start');
    print $h 'debug';
    like($cont, qr/debug/,      "Debug found");
    like($cont, qr/Test::More/, 'Trace found');
    like($cont, qr/\d{10}/,     'timestamp found');

    #diag( $cont );

    done_testing();
};

subtest "TiedHandler to HANDLE" => sub {

    use_ok('MordaX::WatchHandle');

    my $backup;
    open($backup, '>&', STDERR);

    my $buff = "";
    close(STDERR);
    open(STDERR, '>', \$buff);

    my $h = \do { local *XCOM };
    tie(*$h, 'MordaX::WatchHandle', \*STDERR);

    #diag('' . $h ." AND " . *$h );
    #ok( *$h->can('watch_dummy'), 'Its a watcher' );

    #diag( tied( *$h ) );
    is(ref(tied(*$h)), 'MordaX::WatchHandle');
    is(ref($h),        'GLOB');

    print STDERR "debug";
    like($buff, qr/debug/);
    unlike($buff, qr/\d{10}/, 'No TimeSTamp');

    print $h "debug X2";

    like($buff, qr/debug X2/);
    like($buff, qr/\d{10}/, 'TimeSTamp');

    close(STDERR);
    open(STDERR, '>&', \$backup);    #& still opened handler
    is(fileno(STDERR), 2, 'STDERR is stil 2');

    done_testing();
};

subtest "TIETO STDERR" => sub {
    #local *STDERR;
    tie(*STDERR, 'MordaX::WatchHandle', \*STDERR);
    is(fileno(*STDERR), 2, 'fileno saves');
    print STDERR 'debug';
    done_testing();
};

#subtest "FORK" => sub

done_testing();

sub flush {
    my ($fh) = shift;
    my $old_fh = select $fh;
    $| = 1;
    select $old_fh;
}

