package Test::FlagsAllowed;
use rules;
use MP::Stopdebug;
use MP::Utils;
use MordaX::Conf;
use MP::Logit qw(dmp logit);
use TestHelper qw(no_register);

sub handler {
    my ($req, $data, $postargs) = @_;
    my $flag_desc = MP::Utils::file_read(MordaX::Conf->get('RootDir') . '/flags_allowed.json') // '';

    my $page = $data->{Page};
    $page->{flags} = $$flag_desc;

    return TestHelper::resp($req, 'test/flags_allowed.html', $data);
}

1;
