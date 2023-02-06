package Test::Xiva;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);

#use MordaX::Logit;
#use MordaX::Utils;
use MordaX::Conf;
use TestHelper qw(no_register);

sub handler {
    &xiva;
}

sub xiva {
    my ($req, $data, $post) = @_;

    my $page = $data->{Page};
    my $get  = $req->{'Getargshash'};

    $page->{XivaUrl} = MordaX::Conf->get('XivaUrl');

    return TestHelper::resp($req, 'test/xiva.html', $data);
}

1;
