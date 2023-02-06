package Handler::Vps::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

#use MP::Logit qw(logit dmp);

use Handler::Vps;

sub test_parse_vp_ids : Test(27) {
    my $self = shift;

    *parse_vp_ids = \&Handler::Vps::parse_vp_ids;

    my @data = (
        ['MordaV3View', ['Morda', 3, 'mordav3']],
        ['MordaV1View', ['Morda', 1, 'morda']],
        ['MordaV7View', ['Morda', 7, 'mordav7']],
        ['ru.yandex.viewport.morda.NewsV1View', ['News', 1, 'morda']],
        ['ru.yandex.viewport.morda.AppsV1View', ['Apps', 1, 'morda']],
        ['ru.yandex.viewport.mordav3.InformerV3View', ['Informer', 3, 'mordav3']],
        ['ru.yandex.viewport.mordav3.MovieV3View', ['Movie', 3, 'mordav3']],
        ['ru.yandex.viewport.mordav7.TvView', ['Tv', 7, 'mordav7']], 
        ['ru.yandex.viewport.mordav7.NewsView', ['News', 7, 'mordav7']],
    );

    for (@data) {
        my ($block, $version, $module) = parse_vp_ids({Getargshash => {vp_ids => $_->[0]}});
        ok($block eq $_->[1][0]);
        ok($version eq $_->[1][1]);
        ok($module eq $_->[1][2]);
    }
}

1;
