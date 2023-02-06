package Handler::NTP::Banner::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use Handler::NTP::Banner;
use MordaX::Banner::Direct;

use MP::Logit qw(dmp logit traceit);

sub setup : Test(setup) {
    my $self = shift;

    my $req = MordaX::Req->new();
    $self->{direct} = MordaX::Banner::Direct->new($req);
    $self->{req} = $req;
}

sub test : Test(0) {
    return;
}

1;