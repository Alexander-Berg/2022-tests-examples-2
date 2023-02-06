package MordaX::Block::Topnews_extended::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::Block::Topnews_extended;
use MordaX::Input;
use MordaX::Req;
use MordaX::YCookie;
use MP::DTS::UserSettings;
use MP::Time;

use constant {
    HOUR => 60 * 60,
    DAY  => 24 * 60 * 60,
};

sub test_is_first_visit : Test(5) {
    my ($self) = @_;

    my ($req, $result, $expected, $desc);
    my $day_start_ts = MP::Time::iso_to_ts('2021-09-13T00:00:00') + MordaX::Block::Topnews_extended::DAY_START_HOUR * 60 * 60;

    {
        $desc = 'no user data, no cookies';
        $req = MordaX::Req->new();
        $expected = 0;

        $result = MordaX::Block::Topnews_extended::_is_first_visit($req);
        is($result, $expected, $desc);
    }

    {
        $desc = 'cookies timestamp';
        $req = MordaX::Req->new();
        $expected = 0;

        $req->{time} = $day_start_ts - 2 * HOUR;
        MordaX::Input::input_time(undef, $req);

        local $req->{YCookies} = MordaX::YCookie->new($req);
        $req->{YCookies}->setyp(MordaX::Block::Topnews_extended::NEXT_DAY_START_COOKIE, 1, $day_start_ts);

        $result = MordaX::Block::Topnews_extended::_is_first_visit($req);
        is($result, $expected, $desc);
    }

    {
        $desc = 'cookies timestamp stale';
        $req = MordaX::Req->new();
        $expected = 1;

        $req->{time} = $day_start_ts + 2 * HOUR;
        MordaX::Input::input_time(undef, $req);

        local $req->{YCookies} = MordaX::YCookie->new($req);
        $req->{YCookies}->setyp(MordaX::Block::Topnews_extended::NEXT_DAY_START_COOKIE, 1, $day_start_ts);

        $result = MordaX::Block::Topnews_extended::_is_first_visit($req);
        is($result, $expected, $desc);
    }

    no warnings qw(redefine);
    local *MP::DTS::UserSettings::get_result = sub {
        bless({}, 'MP::DTS::UserSettings')
    };
    local *MP::DTS::UserSettings::get = sub {
        return $day_start_ts if ($_[1] eq MordaX::Block::Topnews_extended::NEXT_DAY_START_DATASYNC_KEY);
    };

    {
        $desc = 'DTS timestamp';
        $req = MordaX::Req->new();
        $expected = 0;

        $req->{time} = $day_start_ts - 2 * HOUR;
        MordaX::Input::input_time(undef, $req);

        $result = MordaX::Block::Topnews_extended::_is_first_visit($req);
        is($result, $expected, $desc);
    }

    {
        $desc = 'DTS timestamp stale';
        $req = MordaX::Req->new();
        $expected = 1;

        $req->{time} = $day_start_ts + 2 * HOUR;
        MordaX::Input::input_time(undef, $req);

        $result = MordaX::Block::Topnews_extended::_is_first_visit($req);
        is($result, $expected, $desc);
    }

}

1;
