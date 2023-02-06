package Handler::Api::WelcomeTab::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MP::Logit qw(logit dmp);

use Handler::Api::WelcomeTab;

sub test_convert_time_to_seconds_of_day : Test(3) {
    my $self = shift;

    no warnings qw(redefine);
    local *convert_time_to_seconds_of_day = \&Handler::Api::WelcomeTab::convert_time_to_seconds_of_day;

    is(convert_time_to_seconds_of_day('abc'), undef, 'abc');
    is(convert_time_to_seconds_of_day('0:00'), 0, '0:00');
    is(convert_time_to_seconds_of_day('3:15'), 11700, '3:15');
}

sub test_parse_time_interval : Test(5) {
    my $self = shift;

    no warnings qw(redefine);
    local *parse_time_interval = \&Handler::Api::WelcomeTab::parse_time_interval;

    is(parse_time_interval(undef), undef, 'undef');
    is(parse_time_interval('abc'), undef, 'abc');
    is(parse_time_interval('00:10-00:00'), undef, '00:10-00:00');
    is(parse_time_interval('00:00-00:00'), undef, '00:00-00:00');

    my $result = {
        min_time_of_day => 0,
        max_time_of_day => 36600,
    };
    is_deeply(parse_time_interval('00:00-10:10'), $result, '00:00-10:10');
}

sub test_get_time_intervals : Test(4) {
    my $self = shift;

    no warnings qw(redefine);
    local *get_time_intervals = \&Handler::Api::WelcomeTab::get_time_intervals;
    local *Handler::Api::WelcomeTab::logit = sub { };

    #
    # undefined allowed_time_intervals
    #

    is(get_time_intervals({}), undef, 'undefined allowed_time_intervals');

    #
    # $data->{allowed_time_intervals} = "00:00-10:10"
    #

    my $input = {
        allowed_time_intervals => '00:00-10:10',
    };
    my $result = [
        {
            min_time_of_day => 0,
            max_time_of_day => 36600,
        },
    ];
    is_deeply(get_time_intervals($input), $result, '$data->{allowed_time_intervals} = "00:00-10:10"');

    #
    # $data->{allowed_time_intervals} = "00:00-10:10 12:00-19:11"
    #

    $input = {
        allowed_time_intervals => '00:00-10:10 12:00-19:11',
    };
    $result = [
        {
            min_time_of_day => 0,
            max_time_of_day => 36600,
        },
        {
            min_time_of_day => 43200,
            max_time_of_day => 69060,
        }
    ];
    is_deeply(get_time_intervals($input), $result, '$data->{allowed_time_intervals} = "00:00-10:10 12:00-19:11"');

    #
    # $data->{allowed_time_intervals} = "00:00-10:10 12:00-19:11"
    #

    $input = {
        allowed_time_intervals => '00:00-10:10 19:11-12:00',
    };
    $result = [
        {
            min_time_of_day => 0,
            max_time_of_day => 36600,
        },
    ];
    is_deeply(get_time_intervals($input), $result, '$data->{allowed_time_intervals} = "00:00-10:10 19:11-12:00"');
}

sub test_get_expiry_date : Test(3) {
    my $self = shift;

    no warnings qw(redefine);
    local *get_expiry_date = \&Handler::Api::WelcomeTab::get_expiry_date;
    local *Handler::Api::WelcomeTab::logit = sub { };

    is(get_expiry_date({}), undef, 'undefined till');
    is(get_expiry_date({till => 'abc'}), undef, '$data->{till} => "abc"');
    is(get_expiry_date({till => '2024-05-30 20:50'}), 1717102200, '$data->{till} => 2024-05-30 20:50');
}

1;