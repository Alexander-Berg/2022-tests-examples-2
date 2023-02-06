package Jobs::test_inconsistency;
use lib::abs qw(..);

use utf8;
#use common::sense;
use strict;
use warnings;
use starter;

use WADM::Utils;
use FakeInput;
use Data::Dumper;
use File::Spec;
use Storable;

sub run {
#    export();
#    failed();
    #
    starter::init_wbox();
    starter::init_wadm();

    require WADM::History;
    #starter::init_geobase();
    #starter::init_madm_data();
    my ($r1, $c1) = main::find_widgets(
        filter => {
            'in_regional'  => 1,
            'with_tags_v2' => 1,
        },
        callback => \&process_widget,
        #            limit => 10,
    );
    my ($r2, $c2) = main::find_widgets(
        filter => {
            'in_catalog'   => 1,
            'with_tags_v2' => 1,
        },
        callback => \&process_widget,
        #            limit => 10,
    );

}
our $processed_widgets = {};

sub process_widget {
    my $widget = shift;

    #skip processed
    return if $processed_widgets->{$widget->id()};
    $processed_widgets->{$widget->id()} = 1;
    my $changed = 0;
    unless (WADM::Utils::test_widget_programs_consistence($widget)) {
        #what case do we have?
        $changed = 1;
        my $cat = WADM::Utils::get_widget($widget->id(), 'catalog');
        my $reg = WADM::Utils::get_widget($widget->id(), 'regional');

        unless ($cat or $reg) {
            WADM::Utils::exclude_widget_from_programs(
                $widget,
                'Повторное исключение из-за технических трудностей на 
                  стороне Яндекса, причину изначального исключения вы можете 
                  узнать у модераторов', FakeInput->new(login => 'auto')
            );
            logit('debug', "widget " . $widget->id() . " repeared by excluding");
        } else {
            logit('debug', "widget " . $widget->id() . " has custom case of inconsistency");
        }

    }
    unless (WADM::Utils::test_cached_consistence($widget)) {
        #repeared i hope
        $changed = 1;
    }

    if ($changed) {
        main::widget_update($widget);
    }

}

