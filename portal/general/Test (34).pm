package MordaX::Block::Banner_smart::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Block::Banner_smart;
use MordaX::Logit;
use Geo::Utils;


sub _startup : Test(startup) {}

sub _setup : Test(setup) {}

sub test__getdata_smartbanner : Test(1) {
    my $self = shift;

    *GetData_smartbanner = \&MordaX::Block::Banner_smart::GetData_smartbanner;

    no warnings qw(redefine experimental::smartmatch);

    local *Req::new = sub {
        return $self;
    };
    local *FakeBlock::Banner_smart::new = sub {
        return $self;
    };

    #
    # smartbanner from bk
    #

    local *MordaX::Options::options = sub {
        return 0 if ($_[0] eq 'smartbanner_from_madm');
    };
    local *MordaX::Block::Banner_smart::get_banner = sub {
        if ($_[1] eq 'smartbanner') {
            return {
                icon_1 => 'https://avatars.mds.yandex.net/get-direct-picture/98965/2htKfGAkNXtCxVX0deKxLA/orig',
                icon_2 => 'https://avatars.mds.yandex.net/get-direct-picture/98966/2htKfGAkNXtCxVX0deKxLA/orig',
                icon_3 => 'https://avatars.mds.yandex.net/get-direct-picture/98967/2htKfGAkNXtCxVX0deKxLA/orig',
                text_1 => 'прогноз погоды',
                text_2 => 'актуальные новости',
                text_3 => 'Алиса',
            };
        }

        return;
    };
    my $req = Req->new();
    my $banner_smart_obj = FakeBlock::Banner_smart->new();
    my $page = {};
    my $result = {
        'Banner_smart' => {
            'show' => 1,
            'distribution' => {
                'smartbanner' => [
                    {
                    'code' => {
                        'features' => [
                                {
                                    'text' => 'прогноз погоды',
                                    'icon' => 'https://avatars.mds.yandex.net/get-direct-picture/98965/2htKfGAkNXtCxVX0deKxLA/orig',
                                },
                                {
                                    'text' => 'актуальные новости',
                                    'icon' => 'https://avatars.mds.yandex.net/get-direct-picture/98966/2htKfGAkNXtCxVX0deKxLA/orig',
                                },
                                {
                                    'icon' => 'https://avatars.mds.yandex.net/get-direct-picture/98967/2htKfGAkNXtCxVX0deKxLA/orig',
                                    'text' => 'Алиса',
                                }
                            ]
                        }
                    }
                ]
            }
        }
    };

    GetData_smartbanner($banner_smart_obj, $req, $page);
    is_deeply($page, $result, 'smartbanner from bk');
}

sub test__getdata : Test(7) {
    my $self = shift;

    *GetData = \&MordaX::Block::Banner_smart::GetData;

    no warnings qw(redefine experimental::smartmatch);

    #
    # microdistribution banner from madm
    #

    local *MordaX::Block::Banner_smart::is_enabled_all = sub { 1 };
    local *Req::new = sub {
        return bless(
            {
                MordaZone => 'ru',
                country_id => Geo::Utils::RUSSIA,
                MordaContent => 'touch',
            },
            'MordaX::Req'
        );
    };
    local *FakeBlock::Banner_smart::new = sub {
        return $self;
    };
    local *MordaX::Experiment::AB::flags = sub {
        return $self;
    };
    local *MordaX::Options::options = sub {
        return 1 if ($_[0] eq 'microdistribution_from_madm');
    };
    local *MordaX::Data_get::get_static_data = sub {
        return {
            bk      => 'micro_distr_bro_promo_andr',
            counter => 'small_andr_yabro_dark',
            domain  => 'ru',
            exp     => 'after_smart',
            locale  => 'all',
            product => 'yabro',
            text    => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{44c} \x{42f}.\x{411}\x{440}\x{430}\x{443}\x{437}\x{435}\x{440}",
            theme   => 'dark',
            url     => 'https://redirect.appmetrica.yandex.com/serve/385389167967799764?c=micro_morda&adgroup=main&source_id=micro_morda&creative=dark&click_id={LOGID}&google_aid={GOOGLE_AID_LC}&ios_ifa={IDFA_UC}&bannerid={BID}'
        };
    };
    local *MordaX::Banners::req_set_flag_urls = sub {
        return unless $_[1]->{bk};

        $_[1]->{show_url}  = 'https://yabs.yandex.ru/count/WFKejI';
        $_[1]->{close_url} = 'https://yabs.yandex.ru/count/819/577358608207';

        return;
    };

    my $page = {};
    my $req = Req->new();
    my $banner_smart_obj = FakeBlock::Banner_smart->new();
    my $result = {
        Distrib_small => {
            close_url => 'https://yabs.yandex.ru/count/819/577358608207',
            counter   => 'small_andr_yabro_dark',
            product   => 'yabro',
            show      => 1,
            show_url  => 'https://yabs.yandex.ru/count/WFKejI',
            text      => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{44c} \x{42f}.\x{411}\x{440}\x{430}\x{443}\x{437}\x{435}\x{440}",
            theme     => 'dark',
            url       => 'https://redirect.appmetrica.yandex.com/serve/385389167967799764?c=micro_morda&adgroup=main&source_id=micro_morda&creative=dark&click_id={LOGID}&google_aid={GOOGLE_AID_LC}&ios_ifa={IDFA_UC}&bannerid={BID}',
        },
    };

    GetData($banner_smart_obj, $req, $page);
    is_deeply($page, $result, 'microdistribution banner from madm');

    #
    # microdistribution banner from bk
    #

    local *MordaX::Options::options = sub {
        return if ($_[0] eq 'microdistribution_from_madm');
    };
    local *MordaX::Block::Banner_smart::get_banner = sub {
        if ($_[1] eq 'microdistribution') {
            return {
                bannerid         => '72057604595945957:3140749283403783815',
                close_url        => 'https://yabs.yandex.ru/count/WUOejI_zO5K1vGu051a0eBkzvX1IrmK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8SVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q792l0_-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HO0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS247YdZpCoDAuvP1ymvbB7sP61KORnaLjqY540~1',
                deeplink_url     => '',
                description_text => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{435} \x{42f}\x{43d}\x{434}\x{435}\x{43a}\x{441}",
                icon_app         => 'https://avatars.mds.yandex.net/get-direct-picture/3934366/oEZAjJjiKVs05GOtJ27Umg/orig',
                linkhead         => 'https://yabs.yandex.ru/count/WFyejI_zO3q0hGS0b0m0eBkz5WvffWK0FG4GWY0nJqE-O000000umeeMy0BLew-P1l050Q061BW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAweB47CJll27NW00wUoMBY_4WC20W0IO3hMhg-lJYjAxT90GY9gJpiMVZ8i4-10Lg170X3tf4ip95CqWx9pOy18KY1C4a1Cos1N1YlRieu-y_6FmoHRmFu4Ng1S9cHZG60Bu680Pi1cu6T8P4dbXOdDVSsLoTcLoBt8rCpKjCUWPWC83y1c0mWCD06fid345WuAxAXecqIs4s143kso9f38VpiL6oPoCPIkXdGE24j51Hm40~1',
                linknext         => '=WK8ejI_zO8C0nGa0r12V0BjpWm5054W8OCuPSAZ6ql60ghFtWm6G0Sh7zDJEW8200fW1oiVqr4wu0UQvczaXs06-n_cO0UW1fWAG0-3Knswm0mAe1WIm1u20c3ou1veqyGS009IZwRY0rTdxGSdu2e2r6DaBXrxODTKkbYle39UW3i24FO0Gtw7b7CWG2AWHm8Gzs1A1W1Zf4ip95CqWx9pOc1C8g1EUXVQ8zfA-lnNe58m2s1N1YlRieu-y_6EG5lK1e1RGlzg51e4Nc1VVtUWdm1Uq6h0OukluXGRu69U3-k3PiiFB5u0P6G6W6GIu6V___m7e6O320_0PWC83WHh__t-0wILwDfWQ_F280lKQ0G000B0RPBWR1Gm0usiOlswNM21GWk5GGLSRXDDD8vD3GMQ5G9dZ70F6n084HkdRB9y1~1',
                main_url         => 'https://yabs.yandex.ru/count/WUKejI_zO5K1tGu0H1a0eBkzIqLhCGK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8S012DW1liVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q79-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HK0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS22BphRJR5ZIaVjmyO4wZZx1u5HZ5c1W00~1',
                product          => 'app',
                styles_type      => 'dark',
            };
        }

        return;
    };

    $page = {};
    $result = {
        Distrib_small => {
                icon_app    => 'https://avatars.mds.yandex.net/get-direct-picture/3934366/oEZAjJjiKVs05GOtJ27Umg/orig',
                close_url   => 'https://yabs.yandex.ru/count/WUOejI_zO5K1vGu051a0eBkzvX1IrmK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8SVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q792l0_-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HO0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS247YdZpCoDAuvP1ymvbB7sP61KORnaLjqY540~1',
                text        => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{435} \x{42f}\x{43d}\x{434}\x{435}\x{43a}\x{441}",
                show_url    => 'https://yabs.yandex.ru/count/WFyejI_zO3q0hGS0b0m0eBkz5WvffWK0FG4GWY0nJqE-O000000umeeMy0BLew-P1l050Q061BW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAweB47CJll27NW00wUoMBY_4WC20W0IO3hMhg-lJYjAxT90GY9gJpiMVZ8i4-10Lg170X3tf4ip95CqWx9pOy18KY1C4a1Cos1N1YlRieu-y_6FmoHRmFu4Ng1S9cHZG60Bu680Pi1cu6T8P4dbXOdDVSsLoTcLoBt8rCpKjCUWPWC83y1c0mWCD06fid345WuAxAXecqIs4s143kso9f38VpiL6oPoCPIkXdGE24j51Hm40~1=WK8ejI_zO8C0nGa0r12V0BjpWm5054W8OCuPSAZ6ql60ghFtWm6G0Sh7zDJEW8200fW1oiVqr4wu0UQvczaXs06-n_cO0UW1fWAG0-3Knswm0mAe1WIm1u20c3ou1veqyGS009IZwRY0rTdxGSdu2e2r6DaBXrxODTKkbYle39UW3i24FO0Gtw7b7CWG2AWHm8Gzs1A1W1Zf4ip95CqWx9pOc1C8g1EUXVQ8zfA-lnNe58m2s1N1YlRieu-y_6EG5lK1e1RGlzg51e4Nc1VVtUWdm1Uq6h0OukluXGRu69U3-k3PiiFB5u0P6G6W6GIu6V___m7e6O320_0PWC83WHh__t-0wILwDfWQ_F280lKQ0G000B0RPBWR1Gm0usiOlswNM21GWk5GGLSRXDDD8vD3GMQ5G9dZ70F6n084HkdRB9y1~1',
                url         => 'https://yabs.yandex.ru/count/WUKejI_zO5K1tGu0H1a0eBkzIqLhCGK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8S012DW1liVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q79-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HK0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS22BphRJR5ZIaVjmyO4wZZx1u5HZ5c1W00~1',
                theme       => 'dark',
                counter     => 'app',
                product     => 'app',
                show        => 1,
        },
    };

    GetData($banner_smart_obj, $req, $page);
    is_deeply($page, $result, 'microdistribution banner from bk with valid product=app');

    local *MordaX::Block::Banner_smart::get_banner = sub {
        if ($_[1] eq 'microdistribution') {
            return {
                bannerid         => '72057604595945957:3140749283403783815',
                close_url        => 'https://yabs.yandex.ru/count/WUOejI_zO5K1vGu051a0eBkzvX1IrmK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8SVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q792l0_-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HO0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS247YdZpCoDAuvP1ymvbB7sP61KORnaLjqY540~1',
                deeplink_url     => '',
                description_text => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{435} \x{42f}\x{43d}\x{434}\x{435}\x{43a}\x{441}",
                icon_app         => 'https://avatars.mds.yandex.net/get-direct-picture/3934366/oEZAjJjiKVs05GOtJ27Umg/orig',
                linkhead         => 'https://yabs.yandex.ru/count/WFyejI_zO3q0hGS0b0m0eBkz5WvffWK0FG4GWY0nJqE-O000000umeeMy0BLew-P1l050Q061BW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAweB47CJll27NW00wUoMBY_4WC20W0IO3hMhg-lJYjAxT90GY9gJpiMVZ8i4-10Lg170X3tf4ip95CqWx9pOy18KY1C4a1Cos1N1YlRieu-y_6FmoHRmFu4Ng1S9cHZG60Bu680Pi1cu6T8P4dbXOdDVSsLoTcLoBt8rCpKjCUWPWC83y1c0mWCD06fid345WuAxAXecqIs4s143kso9f38VpiL6oPoCPIkXdGE24j51Hm40~1',
                linknext         => '=WK8ejI_zO8C0nGa0r12V0BjpWm5054W8OCuPSAZ6ql60ghFtWm6G0Sh7zDJEW8200fW1oiVqr4wu0UQvczaXs06-n_cO0UW1fWAG0-3Knswm0mAe1WIm1u20c3ou1veqyGS009IZwRY0rTdxGSdu2e2r6DaBXrxODTKkbYle39UW3i24FO0Gtw7b7CWG2AWHm8Gzs1A1W1Zf4ip95CqWx9pOc1C8g1EUXVQ8zfA-lnNe58m2s1N1YlRieu-y_6EG5lK1e1RGlzg51e4Nc1VVtUWdm1Uq6h0OukluXGRu69U3-k3PiiFB5u0P6G6W6GIu6V___m7e6O320_0PWC83WHh__t-0wILwDfWQ_F280lKQ0G000B0RPBWR1Gm0usiOlswNM21GWk5GGLSRXDDD8vD3GMQ5G9dZ70F6n084HkdRB9y1~1',
                main_url         => 'https://yabs.yandex.ru/count/WUKejI_zO5K1tGu0H1a0eBkzIqLhCGK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8S012DW1liVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q79-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HK0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS22BphRJR5ZIaVjmyO4wZZx1u5HZ5c1W00~1',
                product          => 'yabro',
                styles_type      => 'dark',
            };
        }

        return;
    };

    $page = {};
    $result = {
        Distrib_small => {
                icon_app    => 'https://avatars.mds.yandex.net/get-direct-picture/3934366/oEZAjJjiKVs05GOtJ27Umg/orig',
                close_url   => 'https://yabs.yandex.ru/count/WUOejI_zO5K1vGu051a0eBkzvX1IrmK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8SVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q792l0_-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HO0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS247YdZpCoDAuvP1ymvbB7sP61KORnaLjqY540~1',
                text        => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{435} \x{42f}\x{43d}\x{434}\x{435}\x{43a}\x{441}",
                show_url    => 'https://yabs.yandex.ru/count/WFyejI_zO3q0hGS0b0m0eBkz5WvffWK0FG4GWY0nJqE-O000000umeeMy0BLew-P1l050Q061BW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAweB47CJll27NW00wUoMBY_4WC20W0IO3hMhg-lJYjAxT90GY9gJpiMVZ8i4-10Lg170X3tf4ip95CqWx9pOy18KY1C4a1Cos1N1YlRieu-y_6FmoHRmFu4Ng1S9cHZG60Bu680Pi1cu6T8P4dbXOdDVSsLoTcLoBt8rCpKjCUWPWC83y1c0mWCD06fid345WuAxAXecqIs4s143kso9f38VpiL6oPoCPIkXdGE24j51Hm40~1=WK8ejI_zO8C0nGa0r12V0BjpWm5054W8OCuPSAZ6ql60ghFtWm6G0Sh7zDJEW8200fW1oiVqr4wu0UQvczaXs06-n_cO0UW1fWAG0-3Knswm0mAe1WIm1u20c3ou1veqyGS009IZwRY0rTdxGSdu2e2r6DaBXrxODTKkbYle39UW3i24FO0Gtw7b7CWG2AWHm8Gzs1A1W1Zf4ip95CqWx9pOc1C8g1EUXVQ8zfA-lnNe58m2s1N1YlRieu-y_6EG5lK1e1RGlzg51e4Nc1VVtUWdm1Uq6h0OukluXGRu69U3-k3PiiFB5u0P6G6W6GIu6V___m7e6O320_0PWC83WHh__t-0wILwDfWQ_F280lKQ0G000B0RPBWR1Gm0usiOlswNM21GWk5GGLSRXDDD8vD3GMQ5G9dZ70F6n084HkdRB9y1~1',
                url         => 'https://yabs.yandex.ru/count/WUKejI_zO5K1tGu0H1a0eBkzIqLhCGK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8S012DW1liVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q79-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HK0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS22BphRJR5ZIaVjmyO4wZZx1u5HZ5c1W00~1',
                theme       => 'dark',
                counter     => 'yabro',
                product     => 'yabro',
                show        => 1,
        },
    };

    GetData($banner_smart_obj, $req, $page);
    is_deeply($page, $result, 'microdistribution banner from bk with valid product=yabro');

    local *MordaX::Block::Banner_smart::get_banner = sub {
        if ($_[1] eq 'microdistribution') {
            return {
                bannerid         => '72057604595945957:3140749283403783815',
                close_url        => 'https://yabs.yandex.ru/count/WUOejI_zO5K1vGu051a0eBkzvX1IrmK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8SVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q792l0_-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HO0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS247YdZpCoDAuvP1ymvbB7sP61KORnaLjqY540~1',
                deeplink_url     => '',
                description_text => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{435} \x{42f}\x{43d}\x{434}\x{435}\x{43a}\x{441}",
                icon_app         => 'https://avatars.mds.yandex.net/get-direct-picture/3934366/oEZAjJjiKVs05GOtJ27Umg/orig',
                linkhead         => 'https://yabs.yandex.ru/count/WFyejI_zO3q0hGS0b0m0eBkz5WvffWK0FG4GWY0nJqE-O000000umeeMy0BLew-P1l050Q061BW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAweB47CJll27NW00wUoMBY_4WC20W0IO3hMhg-lJYjAxT90GY9gJpiMVZ8i4-10Lg170X3tf4ip95CqWx9pOy18KY1C4a1Cos1N1YlRieu-y_6FmoHRmFu4Ng1S9cHZG60Bu680Pi1cu6T8P4dbXOdDVSsLoTcLoBt8rCpKjCUWPWC83y1c0mWCD06fid345WuAxAXecqIs4s143kso9f38VpiL6oPoCPIkXdGE24j51Hm40~1',
                linknext         => '=WK8ejI_zO8C0nGa0r12V0BjpWm5054W8OCuPSAZ6ql60ghFtWm6G0Sh7zDJEW8200fW1oiVqr4wu0UQvczaXs06-n_cO0UW1fWAG0-3Knswm0mAe1WIm1u20c3ou1veqyGS009IZwRY0rTdxGSdu2e2r6DaBXrxODTKkbYle39UW3i24FO0Gtw7b7CWG2AWHm8Gzs1A1W1Zf4ip95CqWx9pOc1C8g1EUXVQ8zfA-lnNe58m2s1N1YlRieu-y_6EG5lK1e1RGlzg51e4Nc1VVtUWdm1Uq6h0OukluXGRu69U3-k3PiiFB5u0P6G6W6GIu6V___m7e6O320_0PWC83WHh__t-0wILwDfWQ_F280lKQ0G000B0RPBWR1Gm0usiOlswNM21GWk5GGLSRXDDD8vD3GMQ5G9dZ70F6n084HkdRB9y1~1',
                main_url         => 'https://yabs.yandex.ru/count/WUKejI_zO5K1tGu0H1a0eBkzIqLhCGK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8S012DW1liVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q79-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HK0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS22BphRJR5ZIaVjmyO4wZZx1u5HZ5c1W00~1',
                product          => 'bro',
                styles_type      => 'dark',
            };
        }

        return;
    };

    $page = {};
    $result = {};

    my $error = {
        type => undef,
        msg => undef,
    };

    local *MordaX::Block::Banner_smart::logit = sub {
        $error->{type} = $_[0];
        $error->{msg} = $_[1];
    };

    GetData($banner_smart_obj, $req, $page);

    is($error->{type}, 'nodata', 'error type is ok');
    is($error->{msg}, '[microdistribution] No valid banner product=bro from bk. Banner with id=72057604595945957:3140749283403783815 was rejected', 'error msg is ok');
    is_deeply($page, $result, 'microdistribution banner from bk without valid product=bro');

    local *MordaX::Options::options = sub {
        return 0 if ($_[0] eq 'smartbanner_from_madm');
        return 1 if ($_[0] eq 'disable_check_bk_microdistribution_valid_banner_product');
    };


    local *MordaX::Block::Banner_smart::get_banner = sub {
        if ($_[1] eq 'microdistribution') {
            return {
                bannerid         => '72057604595945957:3140749283403783815',
                close_url        => 'https://yabs.yandex.ru/count/WUOejI_zO5K1vGu051a0eBkzvX1IrmK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8SVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q792l0_-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HO0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS247YdZpCoDAuvP1ymvbB7sP61KORnaLjqY540~1',
                deeplink_url     => '',
                description_text => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{435} \x{42f}\x{43d}\x{434}\x{435}\x{43a}\x{441}",
                icon_app         => 'https://avatars.mds.yandex.net/get-direct-picture/3934366/oEZAjJjiKVs05GOtJ27Umg/orig',
                linkhead         => 'https://yabs.yandex.ru/count/WFyejI_zO3q0hGS0b0m0eBkz5WvffWK0FG4GWY0nJqE-O000000umeeMy0BLew-P1l050Q061BW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAweB47CJll27NW00wUoMBY_4WC20W0IO3hMhg-lJYjAxT90GY9gJpiMVZ8i4-10Lg170X3tf4ip95CqWx9pOy18KY1C4a1Cos1N1YlRieu-y_6FmoHRmFu4Ng1S9cHZG60Bu680Pi1cu6T8P4dbXOdDVSsLoTcLoBt8rCpKjCUWPWC83y1c0mWCD06fid345WuAxAXecqIs4s143kso9f38VpiL6oPoCPIkXdGE24j51Hm40~1',
                linknext         => '=WK8ejI_zO8C0nGa0r12V0BjpWm5054W8OCuPSAZ6ql60ghFtWm6G0Sh7zDJEW8200fW1oiVqr4wu0UQvczaXs06-n_cO0UW1fWAG0-3Knswm0mAe1WIm1u20c3ou1veqyGS009IZwRY0rTdxGSdu2e2r6DaBXrxODTKkbYle39UW3i24FO0Gtw7b7CWG2AWHm8Gzs1A1W1Zf4ip95CqWx9pOc1C8g1EUXVQ8zfA-lnNe58m2s1N1YlRieu-y_6EG5lK1e1RGlzg51e4Nc1VVtUWdm1Uq6h0OukluXGRu69U3-k3PiiFB5u0P6G6W6GIu6V___m7e6O320_0PWC83WHh__t-0wILwDfWQ_F280lKQ0G000B0RPBWR1Gm0usiOlswNM21GWk5GGLSRXDDD8vD3GMQ5G9dZ70F6n084HkdRB9y1~1',
                main_url         => 'https://yabs.yandex.ru/count/WUKejI_zO5K1tGu0H1a0eBkzIqLhCGK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8S012DW1liVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q79-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HK0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS22BphRJR5ZIaVjmyO4wZZx1u5HZ5c1W00~1',
                product          => 'search-app',
                styles_type      => 'dark',
            };
        }

        return;
    };

    $page = {};
    $result = {
        Distrib_small => {
                icon_app    => 'https://avatars.mds.yandex.net/get-direct-picture/3934366/oEZAjJjiKVs05GOtJ27Umg/orig',
                close_url   => 'https://yabs.yandex.ru/count/WUOejI_zO5K1vGu051a0eBkzvX1IrmK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8SVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q792l0_-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HO0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS247YdZpCoDAuvP1ymvbB7sP61KORnaLjqY540~1',
                text        => "\x{423}\x{441}\x{442}\x{430}\x{43d}\x{43e}\x{432}\x{438}\x{442}\x{435} \x{42f}\x{43d}\x{434}\x{435}\x{43a}\x{441}",
                show_url    => 'https://yabs.yandex.ru/count/WFyejI_zO3q0hGS0b0m0eBkz5WvffWK0FG4GWY0nJqE-O000000umeeMy0BLew-P1l050Q061BW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAweB47CJll27NW00wUoMBY_4WC20W0IO3hMhg-lJYjAxT90GY9gJpiMVZ8i4-10Lg170X3tf4ip95CqWx9pOy18KY1C4a1Cos1N1YlRieu-y_6FmoHRmFu4Ng1S9cHZG60Bu680Pi1cu6T8P4dbXOdDVSsLoTcLoBt8rCpKjCUWPWC83y1c0mWCD06fid345WuAxAXecqIs4s143kso9f38VpiL6oPoCPIkXdGE24j51Hm40~1=WK8ejI_zO8C0nGa0r12V0BjpWm5054W8OCuPSAZ6ql60ghFtWm6G0Sh7zDJEW8200fW1oiVqr4wu0UQvczaXs06-n_cO0UW1fWAG0-3Knswm0mAe1WIm1u20c3ou1veqyGS009IZwRY0rTdxGSdu2e2r6DaBXrxODTKkbYle39UW3i24FO0Gtw7b7CWG2AWHm8Gzs1A1W1Zf4ip95CqWx9pOc1C8g1EUXVQ8zfA-lnNe58m2s1N1YlRieu-y_6EG5lK1e1RGlzg51e4Nc1VVtUWdm1Uq6h0OukluXGRu69U3-k3PiiFB5u0P6G6W6GIu6V___m7e6O320_0PWC83WHh__t-0wILwDfWQ_F280lKQ0G000B0RPBWR1Gm0usiOlswNM21GWk5GGLSRXDDD8vD3GMQ5G9dZ70F6n084HkdRB9y1~1',
                url         => 'https://yabs.yandex.ru/count/WUKejI_zO5K1tGu0H1a0eBkzIqLhCGK0LG8GWY0nJqE-O000000umeeMG1H8263E6N2enjBnWAgpzuC1a07An_JKpe20W0AO0Sh7zDHEk07ckPlP8S012DW1liVvc07e0QO2y0BLew-P1f03uDJ7Rh031F050RW6gWF91hNLQZrLI7TqgGU7NjWrrIwMAx07W82OFBW7cZIKe-cuWDNP-q79-0g0jHYg2n1p4xxmXru00EdibYulnF0B0-WCby20W0G_jQkhwzEAqhk04D-XvHoG48YQayx5duoB1CWG2FWG5QWHm8Gzs1A1W1Zf4ip95CqWx9pOy18KY1C4a1Coc1C8g1EUXVQ8zfA-l-WKZ0BO5S6AzkoZZxpyO_2G5lK1e1RGlzg51e4Nc1VVtUWdg1S9m1Uq6h0OukluXGRG60Bu69U3-k3PiiFB5u0Pa1a1e1a4i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJCrBJ7e6O320_0PWC83WHh__t-0wILwDfWQ_F280h0QkxBXx8heylol0VKQ0G000B0RPBWR1HK0b6HWinLEAChpCEHpsLOzYFCI3OUE8nkbrrtTe4HiG7smmI2p-C6IfnyU9GS22BphRJR5ZIaVjmyO4wZZx1u5HZ5c1W00~1',
                theme       => 'dark',
                counter     => 'search-app',
                product     => 'search-app',
                show        => 1,
        },
    };

    GetData($banner_smart_obj, $req, $page);
    is_deeply($page, $result, 'microdistribution banner from bk with disable_check_bk_microdistribution_valid_banner_product');

}

sub yabs { 0 };
sub TargetBlock { 'Banner_smart' };

1;
