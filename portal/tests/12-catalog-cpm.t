#!/usr/bin/env perl

use utf8;
use strict;
use warnings;

use lib::abs '../lib/';
use Test::Most qw(no_plan);

use MordaX::Utils;
use Handler::WCatalog;
use MordaX::Conf;
use MordaX::Cache;
use MordaX::Block::WidgetRubrics;
use Data::Dumper;
use MordaX::Logit qw(dumpit);
#use InitUtils;
use Geo;
use Geo::Utils;

my $search_debug = 0;                                                                                             # || 1;
my @hosts        = (qw{http://search.w-dev2.yandex.net/widgetsjson http://search.wdevx.yandex.ru/widgetsjson});
my @regions      = (qw{
      213
      2
      143
      157
      293
      237
      240
      235
      10734
      10747
      10337
      236
      10752
      39
      });
my @region_names = (qw{ Сургут Королёв Воскресенск Севастополь Серпухов Феодосия Череповец Зеленоград Новороссийск Орехово-Зуево Обнинск
      Свердловск Новосибирск Пермь Стамбул });

ok(!Geo::init(), 'no Geo::init');

REG: foreach my $r_name (@region_names) {
    foreach my $gid (geo()) {
        if (geo($gid, 'name') eq $r_name) {
            push @regions, $gid;
            next REG;
        }
    }
}

#ok($mordax_conf, 'config inited');
#--------------------------------------------
my $alldata = MordaX::Cache->get('widget_rubrics');
ok($alldata, 'widget rubrics data loaded');

#-------------------------------------------------
my $mbwr = MordaX::Block::WidgetRubrics->new();
my ($req, $page) = ({}, {});
my $rubrics = $mbwr->GetData($req, $page);

ok($rubrics, 'rubrics obtained');

my $r_cx = 0;
foreach my $main_rubric (values %{$rubrics->{'path2rub'}}) {
    my $rubric = $main_rubric;
    #print Data::Dumper::Dumper( $rubric );
    $r_cx++;
    #last if $r_cx > 3;
    foreach my $region (@regions) {
        my %search_params = (
            #'order'           => $getargs->{'order'},
            'region' => $region,
            #'l1'              => $interface_lang_id,
        );
        my $geo_tree = Geo::Utils::get_nearest_geo_parents_hash($region);
        #print Dumper($geo_tree);
        #ok( $geo_tree->{city}, 'city ok for region '. $region );
        for (qw/city district country/) {
            $search_params{'region_' . $_} = $geo_tree->{$_};
        }
        my $regional_filter = Handler::WCatalog::GetRegionalSearchFilter($geo_tree);
        if ($regional_filter) {
            $regional_filter = " || ( $regional_filter ) ";
        } else {
            $regional_filter = '';
        }
        my $catalog_filter = '( is_catalog="1" ' . $regional_filter . ')';

        my $searchfunc = Handler::WCatalog::gen_search_func(%search_params, 'fulltext' => 0);
        my $res_hash = {};
        for (my $host_id = 0; $host_id < @hosts; $host_id++) {

            my $host = $hosts[$host_id];
            my $url  = $host;
            #$mordax_conf->{'ConfCache'}{SearchWidgetsBackend} = $url;
            MordaX::Conf->new()->set('SearchWidgetsBackend', $url);

            #local $Mordax::Logit::setuplogging;
            $MordaX::Logit::setuplogging{debug} = $search_debug;
            my ($result_info, $found_ids) = Handler::WCatalog::make_search_request(
                'text'    => $rubric->{'search_string'} . ' && ' . $catalog_filter,
                'how'     => 'usrf',
                'userhow' => $searchfunc,
                'p'       => 1,
                's'       => 12,
            );
            unless (is_array $found_ids ) {
                boilout('search fail')
            }

            unless (scalar @$found_ids) {
                fail("R: $region, Rubric: $rubric->{path}: ! somthing found for host ( $host_id )");
            }
            foreach my $id (@$found_ids) {
                $res_hash->{$id} += $host_id + 1;
            }
        }
        my $res_good_cx = 0;
        my $res_bad_cx  = 0;
        foreach my $id (keys %$res_hash) {
            if ($res_hash->{$id} == 3) {
                $res_good_cx++;
                delete $res_hash->{$id};
            } else {
                #diag("R: $region, Rubric: $rubric->{path}, ID: $id <- $res_hash->{$id}" );
                $res_bad_cx += 0.5;
            }
        }
        my $good_expected = $res_good_cx + $res_bad_cx - 2;
        if ($res_bad_cx > 0) {
            cmp_ok($res_good_cx, '>=', $good_expected, "R: $region, Rubric: $rubric->{path}, good in compare, but has differences");
        } else {
            #ok( 1 , "R: $region, Rubric: $rubric->{path}, full in compare");
        }
        #debug output
        if ($res_bad_cx > 2) {
            foreach my $id (keys %$res_hash) {
                #diag("R: $region, Rubric: $rubric->{path}, ID: $id <- $res_hash->{$id}" );
            }
        }

    }
}

