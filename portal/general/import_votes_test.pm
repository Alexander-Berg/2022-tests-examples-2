#!/usr/bin/perl
package import_votes_test;
use lib::abs qw(./ ../lib);
use rules;

use ExportsBase;
use MordaX::Data_get_simple;
use MordaX::Data_load;
use MP::Logit;

MordaX::Data_load::load_static_exports(qw(votes_auto_test.json));

ExportsBase::processer(
    url => sub { 1 },
    name => 'votes_test',
    save_json => 1,
    process => \&process_data,
);

sub process_data {
    my ($helper, $content, $data, $eb) = @_;

    my $data = MordaX::Data_get_simple::getblockalldata('votes_auto_test');
    $$content = $data->{duma2021} // {};
}
