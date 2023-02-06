package BM::BannersMaker::MakeBanners;

use strict;
use warnings;

use JSON::XS qw();

sub init_process_offer_common {
    my $self = shift;
    $self->{json_obj} = JSON::XS->new->utf8(0);
}

sub begin_prepare_tasks_and_offers {
    my $self = shift;
    $self->{row_count} = 0;
}

sub end_prepare_tasks_and_offers {
    my $self = shift;
    delete $self->{row_count};
}

sub map_prepare_tasks_and_offers {
    my $self = shift;
    $self->{yield}->({
        $self->{ID_FIELD} => $self->{row}->{id},
        come_from => "prepare_tasks_and_offers",
        test_message_with_nl => "abc\ndef",
        row_count => $self->{row_count},
    } => $self->{dst_tables}->{OUTPUT_TABLE});
    $self->{row_count} += 1;
}


sub begin_process_offer_common {
    # nothing to do here
}

sub end_process_offer_common {
    my $self = shift;
    $self->{yield}->({message => "log\tmessage"} => $self->{dst_tables}->{LOG_TABLE});
}

sub map_process_offer {
    my $self = shift;
    $self->{yield}->({
        $self->{ID_FIELD} => $self->{row}->{id},
        stash_data => $self->{stash}->{step},
        come_from => "process_offer",
    } => $self->{dst_tables}->{DONE_TABLE});
}

sub map_offer_finalize {
    my $self = shift;
    $self->{yield}->({
        $self->{ID_FIELD} => $self->{row}->{id},
        stash_data => $self->{stash}->{step},
        come_from => "map_offer_finalize",
    } => $self->{dst_tables}->{DONE_TABLE});
}

1;
