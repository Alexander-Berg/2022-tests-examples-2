package testlib::UserAgent;

use MP::UserAgent;
use base qw(MP::UserAgent);
use DNS;



sub get {
    my $self = shift;
    local *DNS::list_ip_by_name = sub { return ['::1'] };
    return $self->SUPER::get( @_ );
}

1;
