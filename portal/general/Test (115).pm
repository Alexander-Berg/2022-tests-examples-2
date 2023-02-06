package MP::Time::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MP::Time;
use MP::Logit;

sub test_time_regexps : Test(6) {
    no warnings qw(redefine);
    like('00:00', qr/^${MP::Time::time_regexp}$/, '00:00');
    like('7:30', qr/^${MP::Time::time_regexp}$/, '7:30');
    like('23:59', qr/^${MP::Time::time_regexp}$/, '23:59');
    unlike('00', qr/^${MP::Time::time_regexp}$/, 'exp = 00');
    unlike('24:00', qr/^${MP::Time::time_regexp}$/, '24:00');
    unlike('00:99', qr/^${MP::Time::time_regexp}$/, '00:99');
}

sub test_time_interval_regexp : Test(4) {
    like('00:00-00:10', qr/^${MP::Time::time_interval_regexp}$/, '00:00-00:10');
    unlike('00:00:00:10', qr/^${MP::Time::time_interval_regexp}$/, '00:00:00:10');
    unlike('00:00,00:10', qr/^${MP::Time::time_interval_regexp}$/, '00:00,00:10');
    unlike('00-00:10', qr/^${MP::Time::time_interval_regexp}$/, '00-00:10');
}

sub test_time_intervals_regexp : Test(3) {
    like('00:00-00:10 00:20-00:30', qr/^${MP::Time::time_intervals_regexp}$/, '00:00-00:10 00:20-00:30');
    unlike('00:00-00:10-00:20-00:30', qr/^${MP::Time::time_intervals_regexp}$/, '00:00-00:10-00:20-00:30');
    unlike('00:00-00:10/00:20-00:30', qr/^${MP::Time::time_intervals_regexp}$/, '00:00-00:10/00:20-00:30');
}

1;