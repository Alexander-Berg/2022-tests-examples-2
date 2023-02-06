package Test::Smoo::Notification::Sup;
use parent 'Test::Class';

use Test::Most;
use MP::Logit qw(logit dmp);
use rules;

use Storable qw/dclone/;
use MP::Utils;
use utf8;

use Smoo::Conf;
use Smoo::Notification::Sup;
use utf8;

my $request = {
    type              => 'push',
    title             => 'Яндекс',
    body              => 'Завтра возможен снег',
    url               => 'morda://',
    dry_run           => 1,
    id                => 'test',
    content_id        => 'content_id',
    throttle_policies => {
        content_id => 'smoo_content_id_policy',
    },
};

my $receivers = [ 'iid:78184065cd953a76800a3158daf957d8' ];

my $expected = {
    receiver     => ['iid:78184065cd953a76800a3158daf957d8'],
    notification => {
        title => 'Яндекс',
        body  => 'Завтра возможен снег',
        icon  => '',
        link  => 'morda://',
    },
    data => {
        push_id     => 'test',
        content_id  => 'content_id',
    },
    schedule               => 'now',
    adjust_time_zone       => \0,
    ttl                    => Smoo::Conf::get('notification')->{'sup'}->{'default_ttl'},
    project                => 'searchapp',
    max_expected_receivers => Smoo::Conf::get('notification')->{'sup'}->{'max_expected_receivers'},
    throttle_policies      => {
        content_id => 'smoo_content_id_policy',
    },
    spread_interval => Smoo::Conf::get('notification')->{'sup'}->{'spread_interval'} || 0,
    type => 'push',
    transport => 'Native',
    priority => 'norm',
    is_data_only => \0,
};

sub make_request : Test() {
    my $_request = dclone $request;

    my $_expected = dclone $expected;

    my $got = Smoo::Notification::Sup::_make_request($_request, $receivers);
    is_deeply($got, $_expected, 'request is ok. default') or explain { got => $got, expected => $_expected };
}

sub max_expected_receivers: Test() {
    my $_request = dclone $request;
    $_request->{ max_expected_receivers } = 10;

    my $_expected = dclone $expected;
    $_expected->{ max_expected_receivers } = 10;

    my $got = Smoo::Notification::Sup::_make_request($_request, $receivers);
    is_deeply($got, $_expected, 'request is ok. max expected receivers') or explain { got => $got, expected => $_expected };
}

sub content_id: Test() {
    my $_request = dclone $request;
    $_request->{ content_id } = 'content';

    my $_expected = dclone $expected;
    $_expected->{ data }->{ content_id } = 'content';

    my $got = Smoo::Notification::Sup::_make_request($_request, $receivers);
    is_deeply($got, $_expected, 'request is ok. content') or explain { got => $got, expected => $_expected };
}

sub experiment: Test() {
    my $_request = dclone $request;
    $_request->{ exp_id } = ['experiment'];

    my $_expected = dclone $expected;
    $_expected->{ exp_id } = ['experiment'];

    my $got = Smoo::Notification::Sup::_make_request($_request, $receivers);
    is_deeply($got, $_expected, 'request is ok. experiment') or explain { got => $got, expected => $_expected };
}

sub is_numbers: Test() {
    my $_request = dclone $request;
    my $got = Smoo::Notification::Sup::_make_request($_request, $receivers);

    my $json = JSON::XS->new->canonical()->utf8->encode($got);
    my $hash = JSON::XS->new->canonical()->utf8->decode($json);
    ok MP::Utils::is_num($hash->{max_expected_receivers}), 'max_expected_receivers is number';
}

sub expireAt: Test() {
    my $_request = dclone $request;
    $_request->{ expireat } = 1555063696000;

    my $_expected = dclone $expected;
    $_expected->{ data }->{ expireAt } = 1555063696000;

    my $got = Smoo::Notification::Sup::_make_request($_request, $receivers);
    is_deeply($got, $_expected, 'request is ok. expireAt') or explain { got => $got, expected => $_expected };
}

sub dev_send: Tests() {
    my $got = Smoo::Notification::Sup::_send({});
    ok $got->{error} =~ m/connect to localhost:5000/ or explain $got;

    local Smoo::Conf::get('notification')->{'sup'}->{url_push} = 'https://push-beta.n.yandex-team.ru/tags/count?e=';
    $got = Smoo::Notification::Sup::_send({});
    ok $got->{error} =~ m/Using production configuration on dev environment/ or explain $got;
}

sub meta: Test() {
    my $_request = dclone $request;
    $_request->{ meta } = { geo => 213 };

    my $_expected = dclone $expected;
    $_expected->{ meta } = { geo => 213 };

    my $got = Smoo::Notification::Sup::_make_request($_request, $receivers);
    is_deeply($got, $_expected, 'request is ok. meta') or explain { got => $got, expected => $_expected };
}

1;
