package MordaX::Block::Ski::Data::Test;

use Test::Most;
use base qw(Test::Class);

use MordaX::Options;
use MordaX::Block::Ski::Data;
use rules;

sub test_get_item_distance : Test(1) {
    my ($self) = @_;

    my $items = [
        {
            # Красная поляна
            lat => 43.671977,
            lon => 40.194585,
            radius => 45000,
        },
        {
            # Где-то между Адлером и Красной Поляной
            lat => 43.617974,
            lon => 40.059843,
            radius => 1000,
        },
        {
            items => [
                {
                    # Роза-Хутор
                    lat => 43.632117,
                    lon => 40.316111,
                    radius => 1000,
                },
                {
                    # Эсто-Садок
                    lat => 43.685056,
                    lon => 40.256059,
                    radius => 1500,
                },
            ],
        },
    ];

    my ($lat, $lon) = (43.676240, 40.244043); # возле Эсто-Садка
    my $expected = [4006, MordaX::Block::Ski::Data::INF(), 1376];

    my $got = [ map { MordaX::Block::Ski::Data::get_item_distance($lat, $lon, $_) }  @$items ];
    is_deeply($got, $expected);
}

sub test_calculate_one_item_distance : Test(1) {
    my ($self) = @_;

    my $item = {
        id => '1214311519',

        # Красная поляня
        lat => 43.668791,
        lon => 40.258294,
        radius => 20000,

        coordinates => [
            {
                # Адлер
                lat => 43.42907,
                lon => 39.936294,
                radius => 20000
            },
            {
                # Где-то в центре Сочи
                lat => 43.581763,
                lon => 39.719647,
                radius => 20000
            }
        ]
    };

    my $coordiantes = [
        {lat => 43.666123, lon => 40.248345}, # в пределах курорта Красная Полянаа
        {lat => 43.411260, lon => 39.948796}, # Олимпийский парк
        {lat => 43.581862, lon => 39.721727}, # Морской вокзал
        {lat => 43.446973, lon => 39.946624}, # Аэропорт Сочи
        {lat => 44.419105, lon => 38.210835}, # дворец Путина
    ];

    my $expected = [853, 2223, 167, 2158, MordaX::Block::Ski::Data::INF()];
    my $got = [ map { MordaX::Block::Ski::Data::calculate_one_item_distance($_->{lat}, $_->{lon}, $item) }  @$coordiantes ];
    is_deeply($got, $expected);
}

1;
