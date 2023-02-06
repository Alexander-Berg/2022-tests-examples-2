package MordaX::Block::Shortcuts::Subreqs::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Banners;
use MordaX::Block::Shortcuts::Subreqs;
use MordaX::Options;
use MordaX::Req;
use MP::Logit;

no  warnings 'experimental::smartmatch';

sub test_substitute_values : Test(1) {
    my ($self) = @_;

    my $test_values = {
        '<<puid>>'      => sub { 12345 },
        '<<yandexuid>>' => sub { 'asdf' },
        '<<did>>'       => sub { undef },
    };

    my $in = {
        key1 => undef,
        key2 => {
            key1 => undef,
            key2 => {key => '<<did>>'},
            key3 => ['<<yandexuid>>'],
            key4 => '<<puid>>',
            key5 => '<<yandexuid>>', 
            key6 => '<<did>>',
            '<<puid>>' => 42,
        },
        key3 => [ undef, {}, [], '<<puid>>', '<<yandexuid>>', '<<did>>', '<<fake_did>>', 42],
        key4 => '<<puid>>',
        key5 => '<<yandexuid>>',
        key6 => '<<did>>',
        '<<puid>>' => 42,
    };
    $in->{key2}{key2}{key1} = $in;
    $in->{key7} = $in->{key2}{key2};
    $in->{key8} = $in->{key3};

    my $out = {
        key1 => undef,
        key2 => {
            key1 => undef,
            key2 => {key => undef},
            key3 => ['asdf'],
            key4 => 12345,
            key5 => 'asdf',
            key6 => undef,
            '<<puid>>' => 42,
        },
        key3 => [undef, {}, [], 12345, 'asdf', undef, '<<fake_did>>', 42],
        key4 => 12345,
        key5 => 'asdf',
        key6 => undef,
        '<<puid>>' => 42,
    };
    $out->{key2}{key2}{key1} = $out;
    $out->{key7} = $out->{key2}{key2};
    $out->{key8} = $out->{key3};

    MordaX::Block::Shortcuts::Subreqs::substitute_values({}, $in, $test_values);

    is_deeply($in, $out);
}

1;
