package Test::Handlers;
use rules;
use lib::abs qw(../);
use MP::Stopdebug;
use MP::Logit qw(dmp logit);
use MP::Utils;
use TestHelper qw(no_register);
use Rapid::Base;
use Rapid::Req;
use HandlerFactory;

sub handle {
    my ($r, $req) = @_;
    $req = Rapid::Req->new(req => $req);
    Rapid::Base::run_require_for('handler', 'test_handlers', [qw/input init component block/], $r, $req,);
    my $output = Rapid::Base::get_handler('test_handlers', $r, $req,);
    return TestHelper::jsonresp($req, {JSON => $output}) if $req->{Getargshash}{cleanvars};
    return TestHelper::resp($req, 'test/handlers.html', $output);
}

Rapid::Base::handler 'test_handlers',
  require => {
    input => [qw/geo getargs/],
  },
  call => sub {
    my ($r, $req, $data) = @_;
    my $page = $data->{'Page'} ||= {};

    $page->{handlers}           = $HandlerFactory::handlers_array;
    $page->{interface_uri_hash} = $HandlerFactory::interface_uri_hash;
    $page->{interface_uri_start}     = $HandlerFactory::interface_uri_start;
    $page->{interface_urix_array} = $HandlerFactory::interface_urix_array;

    return $data;
  };

1;
