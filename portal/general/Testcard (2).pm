package MordaX::Block::Assist::Testcard;

use rules;
use MP::Stopdebug;

use MP::Logit qw(dmp logit);
use MP::Utils;

use MordaX::Experiment;
use MordaX::Utils;

sub SubBlockGetData {
    my ($req, $block_hash, $card, $args) = @_;
    return unless $req->{'YandexInternal'} or MordaX::Experiment::is_sid669($req);
    return unless is_hash_size $card->{'data'};
    if (index($card->{'type'}, 'smoo.') != 0) {
        return unless $card->{'feedback'};
        return unless $card->{'feedback'} =~ m/^[a-z0-9.-]++\@[a-z0-9.-]++$/i;
        return unless MordaX::Experiment::on($req, 'assist_divcard', 'assist_divcard_ios');
    }
    return if MordaX::Utils::options('disable_bass_test_cards');
    return $card->{'data'};
}

1;
