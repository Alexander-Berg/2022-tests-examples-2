package Test::Smoo::Event::Push::Appsearch_ios;
use parent 'Test::Smoo::Event::Push';

use Test::Most;
use MP::Logit qw(logit dmp);
use rules;

use Smoo::Event::Push::Appsearch_ios;
use utf8;

sub make : Test(2) {
    my $test = shift;
    for my $case (@{$test->{cases}}) {
        my $input  = $case->{input};
        my $output = $case->{output}->{Appsearch_ios};
        my $push   = Smoo::Event::Push::Appsearch_ios::make(
            l10n => $input->{l10n},
        );
        is_deeply($push, $output);
    }
}
1;
