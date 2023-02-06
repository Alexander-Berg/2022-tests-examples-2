package Test::Dumps;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);
use JSON::XS;
use MordaX::HTTP;
use MordaX::Logit;
use MordaX::Utils;
use MordaX::Conf;
use MordaX::HTTP;
use Geo;
use TestHelper qw(no_register);

sub handler {
    list(@_);
}

sub list {
    my ($req, $data, $post) = @_;

    my $page = $data->{Page};
    my $get  = $req->{'Getargshash'};
    my $host = $req->{'MockDB'} || MordaX::Conf->get('MockDB');

    $host =~ s{^https?://}{}i;

    my $http = MordaX::HTTP->new($req);

    #dmp( $req );

    #logit('debug', "REQ: $req $http", MordaX::HTTP->new( req => $req ));

    if ($host) {
        eval {
            $http->add(
                alias => 'dumps_list',
                url   => "http://" . $host . "/api/v1/dumps/all/?skipFields=data,logsUrl&sort=created&order=-1",
            );

            my $resp = $http->result('dumps_list');

            my $json = JSON::XS->new()->utf8->decode($resp);
            #dmp( $json );

            $page->{dumps} = $json->{data} || [];

        };
        dmp('error', $@) if $@;
    }

    return TestHelper::resp($req, 'test/dumps_list.html', $data);
}

1;

