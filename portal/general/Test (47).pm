package MordaX::Block::Tv::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Utils;
use MordaX::Block::Tv;
use MordaX::Logit qw(logit dmp);

sub test_get_family_id : Test(3) {
    no warnings qw(redefine);
    *get_family_id = \&MordaX::Block::Tv::get_family_id;

    #
    # === undef $channel_id
    #
    is(get_family_id({}, undef), undef, 'undef $channel_id');

    #
    # === tv_ch_struct returned {}
    #
    local *MordaX::Block::Tv::tv_ch_struct = sub { return {}; };
    is(get_family_id({}, undef), undef, 'tv_ch_struct returned {}');

    #
    # === tv_ch_struct returned {family_id_by_channel_id => {123 => 321}}
    #
    *MordaX::Block::Tv::tv_ch_struct = sub { return {family_id_by_channel_id => {123 => 321}}; };
    is(get_family_id({}, 123), 321, 'tv_ch_struct returned {family_id_by_channel_id => {123 => 321}}');
}

sub test_get_href_with_family_id : Test(4) {
    no warnings qw(redefine);
    *get_href_with_family_id = \&MordaX::Block::Tv::get_href_with_family_id;

    #
    # === undef $channel_id or undef $href
    #
    is(get_href_with_family_id({}, 'https://tv.yandex.ru', undef), undef, 'undef $channel_id');
    is(get_href_with_family_id({}, undef, 123), undef, 'undef $href');

    #
    # === undef $family_id
    #
    local *MordaX::Block::Tv::get_family_id = sub { return undef; };
    is(get_href_with_family_id({}, 'https://tv.yandex.ru', 123), undef, 'undef $family_id');

    #
    # === returned https://tv.yandex.ru?family_id=321
    #
    *MordaX::Block::Tv::get_family_id = sub { return 321; };
    is(get_href_with_family_id({}, 'https://tv.yandex.ru', 123), 'https://tv.yandex.ru?family_id=321', 'returned https://tv.yandex.ru?family_id=321');
}

1;