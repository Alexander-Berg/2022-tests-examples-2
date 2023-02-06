package Test::ScriptLog;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);

use MordaX::Logit qw(dmp logit);
use MordaX::Output;

use Rapid::Base (qw/handler/);
use Rapid::Req;

#use POSIX (qw/strftime/);

sub handle {
    my ($r, $req) = @_;
    ## no critic (Variables::RequireInitializationForLocalVars)
    local $MordaX::Logit::setuplogging;
    ## use critic
    MordaX::Logit::setup(0);

    $req = Rapid::Req->new(req => $req);
    Rapid::Base::run_require_for('handler', 'scriptlog', [qw/input init component block/], $r, $req,);
    my $output = Rapid::Base::get_handler('scriptlog', $r, $req,);
    #dmp( $output );

    return MordaX::Output::respond($req, $output, [], 'text/plain');
}

handler 'scriptlog',
  require => {
    input => [qw/getargs/],
  },
  call => sub {
    my ($r, $req, $args) = @_;
    my $get = $req->{'Getargshash'};
    return `tail -n 40 /var/log/www/export_*.log 2>&1`;
  };

1;

