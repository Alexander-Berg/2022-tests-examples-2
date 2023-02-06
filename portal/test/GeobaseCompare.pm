package Test::GeobaseCompare;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);

use TestHelper qw(no_register);

sub handler {
    my ($req, $data) = @_;
    return TestHelper::resp($req, 'test/geobase.compare.html', $data);
}

1;
