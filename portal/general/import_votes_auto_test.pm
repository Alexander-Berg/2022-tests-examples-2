#!/usr/bin/perl
package import_votes_test;
use lib::abs qw(./ ../lib);
use rules;

use ExportsBase;
use MordaX::Data_get;
use MordaX::Data_load;
use MP::Logit;
use MP::Time;

MordaX::Data_load::load_static_exports(qw(vote_events_v2 vote_candidates_v2 vote_regions));

ExportsBase::processer(
    url => sub { 1 },
    name => 'votes_auto_test',
    save_json => 1,
    process => \&process_data,
);

# {
#     "duma2021": {
#         "candidates_info": {
#             "apple": {"name": "«Яблоко»"},
#             "civil_platform": {"name": "«Гражданская платформа»"},
#             "communists_of_russia": {"name": "«Коммунисты России»"},
#             "fair_russia": {"name": "«Справедливая Россия — За правду»"},
#             "green": {"name": "«Зелёные»"},
#             "green_alternative": {"name": "«Зелёная альтернатива»"},
#             "homeland": {"name": "«Родина»"},
#             "kprf": {"name": "Коммунистическая партия Российской Федерации"},
#             "ldpr": {"name": "ЛДПР"},
#             "new_people": {"name": "«Новые люди»"},
#             "party_of_growth": {"name": "«Партия Роста»"},
#             "rppss": {"name": "Российская партия пенсионеров за социальную справедливость"},
#             "rpss": {"name": "Российская партия свободы и справедливости"},
#             "united_russia": {"name": "«Единая Россия»"}
#         },
#         "results": {
#             "by_region": {
#                 "213": {
#                     "candidates": {
#                         "apple": 10.93,
#                         "civil_platform": 8.75,
#                         "communists_of_russia": 4.85,
#                         "fair_russia": 3.32,
#                         "green": 1.97,
#                         "green_alternative": 7.24,
#                         "homeland": 6.41,
#                         "kprf": 6.98,
#                         "ldpr": 5,
#                         "new_people": 6.5,
#                         "party_of_growth": 4.94,
#                         "rppss": 12.89,
#                         "rpss": 12.14,
#                         "united_russia": 7.99
#                     },
#                     "processed_ballots": 93.48,
#                     "turnout": 53.64,
#                     "update_time": 1629802941
#                 }
#             },
#             "total": {
#                 "candidates": {
#                     "apple": 7.95,
#                     "civil_platform": 6.26,
#                     "communists_of_russia": 7.16,
#                     "fair_russia": 2.52,
#                     "green": 2.02,
#                     "green_alternative": 5.36,
#                     "homeland": 9.76,
#                     "kprf": 8.58,
#                     "ldpr": 4.59,
#                     "new_people": 9.77,
#                     "party_of_growth": 4.22,
#                     "rppss": 10.11,
#                     "rpss": 10.89,
#                     "united_russia": 10.67
#                 },
#                 "processed_ballots": 90.70999999999999,
#                 "turnout": 62.94,
#                 "update_time": 1629802941
#             }
#         },
#         "update_time": 1629802941
#     }
# }

sub process_data {
    my ($helper, $content, $data, $eb) = @_;

    my $out;

    my $events = MordaX::Data_get::get_static_data({}, 'vote_events_v2', all => 1);
    my $events_hash = { map { $_->{id} => $_ } @$events };
    for my $event_id ( keys %$events_hash ) {
        my $regions = MordaX::Data_get::get_static_data({}, 'vote_regions', text_key => $event_id);
        for (@$regions) {
            $_->{voters_cnt} = int rand(500000);
        }

        my $candidates = MordaX::Data_get::get_static_data({}, 'vote_candidates_v2', text_key => $event_id);
        for (@$candidates) {
            $_->{weight} = rand(1);
        }

        my $ready = { update_time => scalar time };

        # может пригодиться
        # for my $candidate (@$candidates) {
        #     $ready->{candidates_info}{$candidate->{c_id}} = {name => $candidate->{name}};
        # }

        for my $region (map { $_->{geo} } @$regions) {
            $ready->{results}{by_region}{$region} = generate_region($candidates);
        }
        $ready->{results}{total} = process_total($regions, $ready->{results}{by_region});

        $out->{$event_id} = $ready;
    }

    $$content = $out;

    # dmp('++++ $content: ', $content);

    return 1;
}

sub generate_region {
    my ($candidates_data) = @_;

    my $sum;
    my $candidates;
    for my $candidate (@$candidates_data) {
        $candidates->{$candidate->{c_id}} = $candidate->{weight} * (1.4 - rand(0.8));
        $sum += $candidates->{$candidate->{c_id}} ;
    }

    for my $id (keys %$candidates) {
        $candidates->{$id} *= 100 / ($sum || 1);
        $candidates->{$id} = round($candidates->{$id});
    }

    return {
        processed_ballots => 80 + round(rand(20)),
        turnout => 40 + round(rand(40)),
        update_time => scalar time,
        candidates => $candidates,
    };
}

sub process_total {
    my ($regions, $by_region) = @_;

    my $regions_cnt = { map { $_->{geo} => $_->{voters_cnt} } @$regions };

    my $cnt_sum;
    for my $cnt (values %$regions_cnt) {
        $cnt_sum += $cnt;
    }

    my $candidates;
    my $processed_ballots;
    my $turnout;
    for my $geo (keys %$by_region) {
        my $item = $by_region->{$geo};
        my $weight = $regions_cnt->{$geo} / ($cnt_sum || 1);

        $processed_ballots += $item->{processed_ballots} * $weight;
        $turnout += $item->{turnout} * $weight;
        for my $id (keys %{$item->{candidates}}) {
            $candidates->{$id} += $item->{candidates}{$id} * $weight;
        }
    }

    for my $id (keys %$candidates) {
        $candidates->{$id} = round($candidates->{$id});
    }

    return {
        processed_ballots => round($processed_ballots),
        turnout => round($turnout),
        update_time => scalar time,
        candidates => $candidates,
    };
}

sub round {
    my ($val) = @_;
    return int($val * 100) / 100;
}
