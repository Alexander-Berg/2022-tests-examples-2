package Test::ClearAll;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);

use MordaX::Logit qw(dmp logit);
use MordaX::Utils;
use MordaX::Cache;

use TestHelper qw(no_register);

sub handler {
    my ($req, $data, $post) = @_;

    my $page = $data->{Page};
    $page->{HomePageNoArgs} = $req->{HomePageNoArgs};

    my @all_cookies = @{$req->{'Cookies'}->list()};
    for my $key (@all_cookies) {
        my $val = $req->{'Cookies'}->value($key);

        unless ($key eq 'webauth_oauth_token' ||
            $key eq 'webauth_csrf_token' ) {
            $req->cookies()->set(
                $req,
                -name    => $key,
                -value   => '',
                -domain  => '.' . $req->{'Domain'},
                -path    => '/',
                -secure  => 0,
                -expires => '-3y',
            );
            logit('info', "clear cookie $key");
        }
    }

    return TestHelper::resp($req, 'test/clear-all.html', $data);
}
1;

