#!/usr/bin/perl

use common::sense;
use warnings;

use lib::abs qw(../bin ../lib ../../lib);

use File::Spec;
use Test::More;

use MordaX::Config;

ok(1, "start testng");
require_ok("antivirus.pl");


$MordaX::Config::DevInstance = 1;
ok( environment() );


my $job_test_resp = Antivirus::get_antivirus_job_answer( { id => 21903 } );
ok( $job_test_resp->{ok}, 'ok flag set'   );
ok( $job_test_resp->{text}, 'ok flag set' );

subtest "Process job " => sub {
    local $main::devmode = 0;
    is( Antivirus::is_devmode() ,  0, 'no devmode');

    my $job_21902  = read_job( 21902 );
    my $job_result = Antivirus::preprocess_job( 
        { id => 21902, },
        {
            ok => 1,
            url => 'autotest',
            text => $job_21902,
        },
        quid => 'auto',
    );
    is( $job_result->{ok}, 0  , 'in progress_ok');
    done_testing();
};    

subtest "Job managment" => sub {
    my $state = Antivirus::currentstate();
    $state->{fast} = [ { id => 1, 'time' => time() - 10 }, { id => 2, 'time' => time - 5} ];
    $state->{slow} = [ { id => 11, 'time' => time() - 10 }, { id => 12, 'time' => time - 5} ];
    $state->{lastcheckjob} = 0;

    main::checkjobs();

    is( $state->{fast}->[0]->{id} , 2 , "second job stay in queue");
    is( scalar @{ $state->{fast} }, 1 , 'one job in q' );
    is( $state->{slow}->[0]->{id} , 12 , "second job stay in queue");
    is( scalar @{ $state->{slow} }, 1 , 'one job in q' );
    done_testing();
};

subtest "BADJOB" => sub {
    my $state = Antivirus::currentstate();
    my $getter = \&Antivirus::get_antivirus_job_answer;
    is( $getter, \&Antivirus::get_antivirus_job_answer, 'function is same');
    my $badjob_cx = 0;
    my $cx = 0;
    $state->{fast} = [ { id => 1, 'time' => time() - 10 }, { id => 2, 'time' => time - 5} ];
    $state->{slow} = [ { id => 11, 'time' => time() - 10 }, { id => 12, 'time' => time - 5} ];
    $state->{lastcheckjob} = 0;

    #is( ref( $getter) , "CODE", 'code');

    *Antivirus::get_antivirus_job_answer = sub {
        my $item = $_[0]; 
        $cx ++;
        if( $item and $item->{id} eq "1" ){
            diag("badjob owerride");
            $badjob_cx ++;
            return { badjob => 1, url => 'test' };
        }
        #return &{$getter}( @_ );
    };

    #*get_antivirus_job_answer = \&Antivirus::get_antivirus_job_answer; 
    isnt( $getter, \&Antivirus::get_antivirus_job_answer, 'function changed');
    #isnt( $getter, \&get_antivirus_job_answer, 'main function changed');
    is( Antivirus::get_antivirus_job_answer(), undef, 'undef on no item');
    $cx = 0;

    diag('call checkjobs');
    main::checkjobs();

    #is( Antivirus::get_antivirus_job_answer(), undef, 'undef on no item');

    is( $state->{fast}->[0]->{id} , 2 , "second job stay in queue");
    is( scalar @{ $state->{fast} }, 1 , 'one job in q' );
    is( $badjob_cx, 1 , 'bad job occured');
    is( $cx, 2, 'function called');
    done_testing() 
};

done_testing();


sub read_job {
    my $id = shift;
    my $path = lib::abs::path("./jobs");
    my $file = File::Spec->catfile( $path , 'antivirus.job.' . $id . ".txt");

    unless( -f $file ){
        fail("job file: $file, not found!");
        return undef;
    }

    open my $fh, '<', $file;
    local $/ = undef;
    my $data = <$fh>;
    close $fh;

    return $data;
}
