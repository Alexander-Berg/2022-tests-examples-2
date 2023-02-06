#!/usr/bin/perl

use Test::More qw(no_plan);
use common::sense;

use common;

use common;

use POSIX;
use Handler::WCatalog;

use MordaX::Block::CatalogCache;
use MordaX::Block::Regional;

use WBOX::Wbox;
use WBOX::Storage::Widgets;
use WBOX::Model::Widget;
use WADM::Index;

#my $w_ids = search( limit => 6 );
#my $w_spb = search( geo => 2, limit => 6 );

#print Data::Dumper->Dump( [ $w_ids ,$w_spb], [ qw/msk_top_id, spb_top_id/ ] );

#dump_csv( $w_ids );
#dump_csv( $w_spb );
pass("wsearch export script")

  ds();
print "spb\n";
ds(geo => 2);
print "ua\n";
ds(geo => 143);
print "e-burg\n";
ds(geo => 54);
print "ufa\n";
ds(geo => 172);
print "n-novgorod\n";
ds(geo => 47);
print "novosibirsk\n";
ds(geo => 65);
print "rostov-na-donu\n";
ds(geo => 39);
print "Perm\n";
ds(geo => 50);
print "Kazan\n";
ds(geo => 43);
print "samara\n";
ds(geo => 51);
print "voronew\n";
ds(geo => 193);

print "R:Fun\n";
ds(rubric => 'fun');
print "R:job\n";
ds(rubric => 'job');
print "R:Sport\n";
ds(rubric => 'sport');

sub ds {
    dump_csv(search(@_));
}

sub search {
    my %attr   = @_;
    my $geo    = $attr{geo} || 213;
    my $tag    = $attr{tag} || '';
    my $label  = $attr{label} || '';
    my $rubric = $attr{rubric} || '';
    my $limit  = $attr{limit} || 24;

    my $req = {
        'GeoByDomainIp' => $geo,
    };
    my $getargs = {
        label  => $label,
        tag    => $tag,
        rubric => $rubric,
    };
    $req->{'Getargshash'} = $getargs;

    my $mbcc       = MordaX::Block::CatalogCache->new();
    my $count_info = Handler::WCatalog::search_regional_counts($req, $mbcc);
    my $reg_info   = Handler::WCatalog::regional_info($req, $count_info);

    my $search_result = Handler::WCatalog::CatalogSearchEngine(
        $req,
        $getargs,
        $reg_info,
        {},
        $limit,
        $mbcc,
    );
    my $widgets = $search_result->{found_widgets};
    my @w_ids = map { $_->id() } @$widgets;

    return \@w_ids;
}

sub dump_csv {
    my $ids = shift;
    require Text::CSV;

    our $csv = Text::CSV->new({
            sep_char => ';',
        }
    );

    $csv->combine('', 'id', 'title', 'users', 'raiting', 'ctr', 'return');
    print $csv->string . "\n";

    for my $id (@$ids) {

        my $widget = WADM::Index::widget_by_wid($id);
        next unless $widget;

        $csv->combine(
            '', $id, $widget->title(), $widget->users(), $widget->rating(), $widget->stat_ctr(),
            $widget->stat_return()
        );
        print $csv->string() . "\n";
    }

}
