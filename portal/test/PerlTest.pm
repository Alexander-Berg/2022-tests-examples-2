package Test::PerlTest;

use rules;
use MP::Logit qw(logit dmp);
use TestHelper qw(no_register);

my $location = {
    'status/' => \&status,
    'add/'    => \&add,
    'report/' => \&report,
};

my $mid = "testdaemon_";

my $conf = MordaX::Conf->new();
my $memd = MordaX::Cache->new();
sub handler {
    my ($req, $data) = @_;
    $data->{Page}->{Instance} =  $MordaX::Config::Instance;

    #dmp( $data->{Page} );
    my $uri = $req->{Uri};
    $uri =~s{/test/t/}{};

    if( $location->{ $uri } ){
        return &{ $location->{ $uri } }( $req, $data );
    }


    #dmp( $req->{Uri} );
    #dmp( $req );
    return TestHelper::resp($req, 'test/perltest.html', $data);
    #local $MordaX::Logit::setuplogging;
    #MordaX::Logit::setup(0);

    #$req = Rapid::Req->new(req => $req);
    #Rapid::Base::run_require_for('handler', 'errorlog', [qw/input init component block/], $r, $req,);
    #my $output = Rapid::Base::get_handler('errorlog', $r, $req,);
    #dmp( $output );

    #return MordaX::Output::respond($req, $output, [], 'text/javascript');
}

sub status {
    my ( $req, $data ) = @_;
    $data->{'JSON'} = {
        respond => 'Disabled HOME-48174',
        ok =>  0,
    };
    return TestHelper::jsonresp($req, $data);
    # my ($req, $data) = @_;
    # $data->{'JSON'} = $memd->get( $mid . 'status' ) || { status => 'stopped' };
    # return TestHelper::jsonresp($req, $data);
}
sub history {
    my ($req, $data) = @_;
    $data->{'JSON'} = {
        respond => 'Disabled HOME-48174',
        ok =>  0,
    };
    return TestHelper::jsonresp($req, $data);
    # my $list = $memd->get( $mid . 'history' ) || '';


    # $data->{'JSON'} = { commands => [ split("\n", $list ) ] };
    # return TestHelper::jsonresp($req, $data);
}
sub add {
    my ( $req, $data ) = @_;
    $data->{'JSON'} = {
        respond => 'Disabled HOME-48174',
        ok =>  0,
    };
    return TestHelper::jsonresp($req, $data);

#     my $command = $req->getargs()->{command};
#     my $respond;
#     for my $dir ( qw/perltest-dev perltest/ ){
#         if( -d "/opt/www/" . $dir ){
#             $respond = `/opt/www/$dir/lib/Tester.pm add $command`;
#         }
#     }
#     my $id;
#     if( $respond =~/id: (\w+)/ ){
#         $id = $1;
#     }
#
#
#     $data->{'JSON'} = {
#         respond => $respond,
#         ok => $id ? 1 : 0,
#         id => $id,
#     };
#
#     return TestHelper::jsonresp($req, $data);
}
sub report {
    my ($req, $data) = @_;
    $data->{'JSON'} = {
        respond => 'Disabled HOME-48174',
        ok =>  0,
    };
    return TestHelper::jsonresp($req, $data);
    # my $id = $req->getargs()->{'id'};
    # my $json = $memd->get( $mid . 'report_' . $id ) || { status => 'notfound' };
    # $json->{running} = $json->{status} eq 'running' ? 1 : 0;
    # $json->{ok}      = $json->{running} || $json->{data}->{ok} ? 1 : 0;
    # $json->{done}    = $json->{status} ~~ [  'done', 'error' ] ? 1 : 0;
    # $data->{'JSON'} = $json;


    # return TestHelper::jsonresp($req, $data);
}

1;
