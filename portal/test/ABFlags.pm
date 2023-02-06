package Test::ABFlags;

use rules;
use MP::Stopdebug;

use MordaX::Experiment::AB::Flags;
use MordaX::Output;

use TestHelper qw(no_register);

sub handler {
    my ($req, $data, $postargs) = @_;

    my $ab_flags = MordaX::Experiment::AB::flags($req)->flags();
    my $flags = [];

    foreach my $flag (keys %$ab_flags) {
        push @$flags, { name => $flag, value => $ab_flags->{$flag}{value} };
    }

    return MordaX::Output::r200json($req, { ab_flags => $flags, handler_logs => $req->{handler_logs} });
}

1;
