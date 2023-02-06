package MordaX::WeatherData::Utils::Test;

use base qw(Test::Class);

use MordaX::WeatherData::Utils;
use MordaX::Req;
use MP::Logit;
use rules;
use Test::Most;

no warnings qw(experimental::smartmatch redefine);

sub test_process_short_forecast : Test(6) {
    my $self = shift;

    my $all_data = {
        forecast => {
            days => [
                {
                    parts => {
                        night => { avgTemperature => 13, icon => 'skc_n' },
                        morning => { avgTemperature => 24, icon => 'skc_n' },
                        day => { avgTemperature => 35, icon => 'skc_n' },
                        evening => { avgTemperature => 26, icon => 'skc_n' },
                    },
                },
                {
                    time => '2022-02-08T00:00:00+03:00',
                    timestamp => 1644181300,
                    parts => {
                        morning => { avgTemperature => 4, icon => 'skc_n' },
                        day => { avgTemperature => 5, icon => 'skc_n' },
                        evening => { avgTemperature => 6, icon => 'skc_n' },
                    },
                },
                {

                    time => '2022-02-09T00:00:00+03:00',
                    timestamp => 1644181400,
                    parts => {
                        night => { avgTemperature => -40, icon => 'skc_n' },
                        morning => { avgTemperature => -25, icon => 'skc_n' },
                        day => { avgTemperature => 2, icon => 'skc_n' },
                        evening => { avgTemperature => -15, icon => 'skc_n' },
                    },
                },
            ],
        },
    };

    my $short_forecast = [
        { name => 'утром', temperature => 24, time => undef, timestamp => undef, icon => "skc_n", day_part => 'morning' },
        { name => 'днём', temperature => 35, time => undef, timestamp => undef, icon => "skc_n", day_part => 'day' },
        { name => 'вечером', temperature => 26, time => undef, timestamp => undef, icon => "skc_n", day_part => 'evening' },
        { name => 'ночью', temperature => undef, time => '2022-02-08T00:00:00+03:00', timestamp => '1644181300', icon => undef, day_part => 'night' },
        { name => 'утром', temperature => 4, time => '2022-02-08T00:00:00+03:00', timestamp => '1644181300', icon => "skc_n", day_part => 'morning' },
        { name => 'днём', temperature => 5, time => '2022-02-08T00:00:00+03:00', timestamp => '1644181300', icon => "skc_n", day_part => 'day' },
        { name => 'вечером', temperature => 6, time => '2022-02-08T00:00:00+03:00', timestamp => '1644181300', icon => "skc_n", day_part => 'evening' },
        { name => 'ночью', temperature => -40, time => '2022-02-09T00:00:00+03:00', timestamp => '1644181400', icon => "skc_n", day_part => 'night' },
        { name => 'утром', temperature => -25, time => '2022-02-09T00:00:00+03:00', timestamp => '1644181400', icon => "skc_n", day_part => 'morning' },
        { name => 'днём', temperature => 2, time => '2022-02-09T00:00:00+03:00', timestamp => '1644181400', icon => "skc_n", day_part => 'day' },
        { name => 'вечером', temperature => -15, time => '2022-02-09T00:00:00+03:00', timestamp => '1644181400', icon => "skc_n", day_part => 'evening' }
    ];

    is_deeply(MordaX::WeatherData::Utils::process_short_forecast({LocalHour => 0}, $all_data), [ @$short_forecast[0..9] ]);
    is_deeply(MordaX::WeatherData::Utils::process_short_forecast({LocalHour => 6}, $all_data), [ @$short_forecast[1..10] ]);
    is_deeply(MordaX::WeatherData::Utils::process_short_forecast({LocalHour => 11}, $all_data), [ @$short_forecast[1..10] ]);
    is_deeply(MordaX::WeatherData::Utils::process_short_forecast({LocalHour => 12}, $all_data), [ @$short_forecast[2..10] ]);
    is_deeply(MordaX::WeatherData::Utils::process_short_forecast({LocalHour => 21}, $all_data), [ @$short_forecast[3..10] ]);
    is_deeply(MordaX::WeatherData::Utils::process_short_forecast({LocalHour => 21}, $all_data, 2), [ @$short_forecast[3..4] ]);
}

1;
