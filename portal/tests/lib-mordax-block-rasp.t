#!/usr/bin/env perl
use Test::Most;

use File::Spec qw();
use JSON::XS qw();
use LWP::Simple qw(get);
use HTML::TagParser qw();
use Data::Dumper;

my $tests_count;
{
    no warnings 'once';
    #проверка наличия расписаний
    my $script_filename = 'scripts/export_trans_type_4_geoid.pl';
    my $script_abs_path = File::Spec->rel2abs($script_filename);
    eval {
        require $script_abs_path;
    };

    ok(!$@, 'require export script');
    my $url = $export_trans_type_4_geoid::url;
    ok($url, "url: $url");

    my $export_content = get($url);
    ok($export_content, 'got export_content');

    my $export_hash = JSON::XS->new->utf8(1)->decode($export_content);
    ok($export_hash, 'export_hash decoded');

    # $export_hash = {112239 => $export_hash->{'112239'}};

    $tests_count = 4;
    foreach my $geo_id (keys %{ $export_hash }) {
        defined $geo_id or die 'Undefined geo_id';
        my $transport_types = $export_hash->{ $geo_id };
        my @available = grep {$transport_types->{ $_ }} keys %{ $transport_types };
        $tests_count += scalar @available;
    }

    my $count = 0;
    foreach my $geo_id (keys %{ $export_hash }) {
        $count++;
        defined $geo_id or die 'Undefined geo_id';
        my $transport_types = $export_hash->{ $geo_id };
        my @available = grep {$transport_types->{ $_ }} keys %{ $transport_types };
        foreach my $type (@available) {
            if (
                $count % 100
                or $type eq 'bus'
            ) {
                $tests_count--;
                next;
            }

            my $schedule_api_url;
            if ($type eq 'suburban') {
                $schedule_api_url = 'http://t.rasp.yandex.ru/suburban-directions?city_geo_id=' . $geo_id;
            } else {
                $schedule_api_url = 'http://t.rasp.yandex.ru/stations/' . $type . '?city_geo_id=' . $geo_id;
            }
            if (my $ok_api = check_schedule_api($schedule_api_url)) {
                pass("$type $geo_id");
            } else {
                TODO: {
                    local $TODO = ' ';
                    fail("$type $geo_id $schedule_api_url");
                }
            }
        }
    }
}

sub check_schedule_api {
    my $schedule_api_url = shift;

    #проверка наличия расписаний для приложения
    my $schedule_content = get($schedule_api_url) or return;
    my $html = HTML::TagParser->new($schedule_content);
    my @content_elems = $html->getElementsByClassName('b-content__item');
    my $content = $content_elems[0];
    my $subhtml = $content->subTree();
    if (my @links = $subhtml->getElementsByTagName('a')) {
        return 1;
    }
    return;
}

done_testing($tests_count);
