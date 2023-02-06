package MordaX::Block::Api_promoblock::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Block::Api_promoblock;
use MordaX::Logit;

sub test_prepare_api_data : Test(1) {
    my ($self) = @_;

    *_prepare_api_data = \&MordaX::Block::Api_promoblock::_prepare_api_data;

    my $in = {
        'data' => {
            'bgcolor' => 'white',
            'bgcolor_dark' => 'black',
            'bgimage' => 'flower.jpg',
            'bgimage_dark' => 'black.jpg',
            'button_text' => 'ok',
            'card_from' => '2020-11-12 00:00',
            'counter' => '132',
            'domain' => 'all',
            'from' => '2020-11-12 00:00',
            'geos' => '225',
            'is_big_card' => '1',
            'lang' => 'ru',
            'link' => '123',
            'subtitle_tanker' => 'yandex.ru',
            'text' => 'text',
            'till' => '2021-11-12 00:00',
            'title' => 'yandex.ru',
            'title_tanker' => 'yandex.ru'
        },
        'processed' => 1,
        'show' => 1
    };
    my $exp = {
        '_card_from_ts' => 1605128400,
        '_card_id_prefix' => 'api_promoblock',
        '_card_id_value' => '132',
        'background_url' => 'https://yastatic.net/s3/home/yandex-app/promo/bground/bigcard/flower.jpg.1.png',
        'background_url_dark' => 'https://yastatic.net/s3/home/yandex-app/promo/bground/bigcard/black.jpg.1.png',
        'bgcolor' => 'white',
        'bgcolor_dark' => 'black',
        'button_text' => 'ok',
        'is_big_card' => '1',
        'text' => 'text',
        'title' => 'yandex.ru',
        'url' => '123'
    };

    my $req = MordaX::Req->new();
    my $result = _prepare_api_data($req, $in);
    is_deeply($result, $exp, 'is_big_card');
}

1;
