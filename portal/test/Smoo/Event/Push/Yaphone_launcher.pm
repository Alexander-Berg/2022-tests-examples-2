package Test::Smoo::Event::Push::Yaphone_launcher;
use parent 'Test::Smoo::Event::Push';

use Test::Most;
use MP::Logit qw(logit dmp);
use rules;

use Smoo::Event::Push::Yaphone_launcher;
use utf8;

sub make : Test(2) {
    my $test = shift;
    for my $case (@{$test->{cases}}) {
        my $input  = $case->{input};
        my $output = $case->{output}->{Yaphone_launcher};
        my $push   = Smoo::Event::Push::Yaphone_launcher::make(
            l10n => $input->{l10n},
        );
        delete $push->{android_features}->{timestamp};
        is_deeply($push, $output) or note explain { got => $push, expected => $output };
    }
}
1;
