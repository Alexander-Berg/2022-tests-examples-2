package Geo::Helper::Test;

use rules;

use Test::Most;
use base qw(Test::Class);


sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok('Geo::Helper');
}

sub test_format_cellid : Test(2) {
    my $self = shift;

    *format_cellid = \&Geo::Helper::format_cellid;

    is(format_cellid('250,99,26895870,11001,0'), '250:99:26895870:11001:0', 'replace , to :');
    is(format_cellid('250:99:26895870:11001:0'), '250:99:26895870:11001:0', 'no replace');
}

sub test_format_wifi : Test(3) {
    my $self = shift;

    *format_wifi = \&Geo::Helper::format_wifi;

    is(format_wifi('04:92:26:37:cd:f8,-88;c0:25:e9:61:a2:3e,-78;'), '04922637cdf8:-88,c025e961a23e:-78', 'mac with :');
    is(format_wifi('04-92-26-37-cd-f8,-88;c0-25-e9-61-a2-3e,-78;'), '04922637cdf8:-88,c025e961a23e:-78', 'mac with -');
    is(format_wifi('04-92-26-37-cd-f8,-88;c0-25-e9-61-a2-3e;'),     '04922637cdf8:-88,c025e961a23e',     'no signal');
}


1;
