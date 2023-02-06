package MordaX::WeatherData::Base::Test;

use base qw(Test::Class);

use MordaX::WeatherData::Base;
use rules;
use Test::Most;

no warnings qw(experimental::smartmatch redefine);

sub test_has_data : Test(7) {
    my $self = shift;

    my $test_cases = [
        { expected => 0, weather_data => undef},
        { expected => 0, weather_data => [1] },
        { expected => 0, weather_data => {} },
        { expected => 0, weather_data => { data => undef, errors => ['error'] } },
        { expected => 0, weather_data => { data => [] } },
        { expected => 0, weather_data => { data => {}, errors => [] } },
        { expected => 1, weather_data => { data => { key => 1 }, errors => [] } },
    ];

    my $wdi = MordaX::WeatherData::Base->new({});
    for my $test (@$test_cases) {
        local *MordaX::WeatherData::Base::get_response = sub { $test->{weather_data} };
        is($wdi->has_data({}), $test->{expected});
    }
}

1;
