package Test::ABCheck;

use rules;
use MP::Stopdebug;

use MP::Logit qw(dmp logit);

use MordaX::Output;

use TestHelper qw(no_register);

sub handler {
    my ($req, $data, $postargs) = @_;
    my $parsed = $data->{Page}{parsed} = parse(@_);
    unless ($parsed->{empty}) {
        $parsed->{src} = $req->{Getargshash}->{condition};
    }
    return TestHelper::resp($req, 'test/abcheck.html', $data);
}

sub parse_handler {
    my ($req, $data, $postargs) = @_;
    MordaX::Output::r200json($req, parse(@_));
}

sub parse {
    my ($req, $data, $postargs) = @_;
    my $condition = $req->{Getargshash}->{condition};
    return { ok => 1, empty => 1 } unless length $condition;

    my $tree = eval { Test::ABCheck::Parser->parse($condition) }
      or return { ok => 0, error => $@ };

    return {
        ok         => 1,
        normalized => $tree->as_string(),
        dump       => $tree->dump(),
        as_hash    => $tree->dump_as_hash(),
    };
}

package Test::ABCheck::Parser;

use mro;

use base qw(MordaX::Experiment::AB::Parser);

sub error {
    my $str    = $_[0]->{str};
    my $pos    = pos($$str);
    my $length = length($$str);
    die  {
        msg => $_[1],
        pos => $pos,
        str => $$str,
    };
}
1;
