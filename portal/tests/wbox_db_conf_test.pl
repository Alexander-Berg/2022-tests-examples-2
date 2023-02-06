#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use lib::abs qw{
  ../lib/
  ../wbox/lib/
};

use WBOX::Utils;
use WBOX::Conf;
use Test::More;

my $wboxConfig = WBOX::Conf->new();
$MordaX::Logit::setuplogging{admin} = 0;
$MordaX::Logit::setuplogging{debug} = 0;

my ($shards, $bases, $dc_settings) = WBOX::Conf->get('Shards', 'Databases', 'DCSettings');

my $dc_etalon = _make_etalon_dc();
is_deeply($dc_settings, $dc_etalon, 'DCSettings');

my $shards_etalon = _make_etalon_shards();
is_deeply($shards, $shards_etalon, 'Shards');

for (qw{ams eto ugr myt fol iva iva2}) {
    $wboxConfig->set('Datacenter', $_);
    my $dc = $wboxConfig->get('Datacenter');
    is($dc, $_, 'DC ' . $dc);
}

for my $dc (qw{ams eto iva ugr}) {
    $wboxConfig->set('Datacenter', $dc);
    my $etalon_create_blocks = _make_etalon_create_blocks($dc);
    isnt(scalar(keys(%{$etalon_create_blocks})), 0, 'Etalon create blocks filled');

    my $create_blocks = {};
    for (0 .. 1000) {
        my ($block_id) = WBOX::Utils::GetBlockID(undef, undef);
        $create_blocks->{$block_id} = 1;
    }
    is_deeply($create_blocks, $etalon_create_blocks, 'Create blocks for dc ' . $dc);

    for my $block (qw{a1 c1 e1 f1}) {
        my $master_etalon = _make_etalon_master($block);
        my $master = WBOX::Utils::GetShardURL($block, 1);
        isnt(scalar(keys(%{$master_etalon->[0]})), 0, 'Master etalon filled');
        is_deeply($master, $master_etalon, 'Check master ' . $block . ' in DC ' . $dc);
    }
}

for my $dc (qw{ams eto}) {
    $wboxConfig->{'ConfCache'}{'Datacenter'} = $dc;
    for my $block (qw{a1 10 e1}) {
        my $replics_etalon = _make_etalon_replics($dc, $block);
        my $replics = WBOX::Utils::GetShardURL($block, 0);
        for my $e_replic (@{$replics_etalon->{'pri'}}) {
            my $replic = shift @{$replics};
            is_deeply($replic, $e_replic, 'Primary replic check DC:' . $dc . ' block: ' . $block);
        }

        is(scalar(@$replics), scalar(@{$replics_etalon->{'sec'}}), 'Number of secondary replics');
        for my $replic (@{$replics}) {
            my $found = 0;
            for my $e_replic (@{$replics_etalon->{'sec'}}) {
                if ($e_replic->{'url'} eq $replic->{'url'}) {
                    is_deeply($replic, $e_replic, 'Secondary replic check DC:' . $dc . ' block: ' . $block);
                    $found = 1;
                    last;
                }
            }
            unless ($found) {
                fail('Secondary replic DC: ' . $dc . ' block: ' . $block);
                next;
            }
        }
    }
}

exit;

sub _make_etalon_replics {
    my $dc    = shift;
    my $block = shift;
    my $rep   = {
        'ams_a1' => {
            'pri' => [{
                    'dc'      => 'ams',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ra1.wboxdb.yandex.net/'
                }],
            'sec' => [],
        },
        'ams_e1' => {
            'pri' => [{
                    'dc'      => 'ams',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ra1.wboxdb.yandex.net/'
                }],
            'sec' => [],
        },

        'eto_a1' => {
            'pri' => [{
                    'dc'      => 'eto',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-re1.wboxdb.yandex.net/'
                }],
            'sec' => [{
                    'dc'      => 'ugr',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ru1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'myt',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-rm1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'fol',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-rn1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'iva',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ri1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'iva2',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ri2.wboxdb.yandex.net/'
                }],
        },
        'eto_e1' => {
            'pri' => [{
                    'dc'      => 'eto',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-re1.wboxdb.yandex.net/'
                }],
            'sec' => [{
                    'dc'      => 'ugr',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ru1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'myt',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-rm1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'fol',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-rn1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'iva',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ri1.wboxdb.yandex.net/'
                }, {
                    'dc'      => 'iva2',
                    'timeout' => '0.1',
                    'url'     => 'http://u1-ri2.wboxdb.yandex.net/'
                }],
          }
    };
    $rep->{'ams_10'} = $rep->{'ams_a1'};
    $rep->{'eto_10'} = $rep->{'eto_a1'};
    return $rep->{$dc . '_' . $block};
}

sub _make_etalon_master {
    my $block   = shift;
    my $masters = {
        'a1' => [{
                'dc'      => 'ugr',
                'timeout' => '0.3',
                'url'     => 'http://u1-se.wboxdb.yandex.net/'
            }],
        'c1' => [{
                'dc'      => 'eto',
                'timeout' => '0.3',
                'url'     => 'http://e1.wboxdb.yandex.net/',
            }],
        'e1' => [{
                'dc'      => 'ams',
                'timeout' => '0.3',
                'url'     => 'http://u1-se.wboxdb.yandex.net/'
            }],
        'f1' => [{
                'dc'      => 'ams',
                'timeout' => '0.3',
                'url'     => 'http://e1.wboxdb.yandex.net/'
            }],
    };
    return $masters->{$block};
}

sub _make_etalon_create_blocks {
    my $dc            = shift;
    my $etalon_blocks = {
        'ugr' => {
            (map { 'a' . $_ => 1 } (0 .. 9)),
            (map { 'b' . $_ => 1 } (0 .. 9)),
        },
        'eto' => {
            (map { 'c' . $_ => 1 } (0 .. 9)),
            (map { 'd' . $_ => 1 } (0 .. 9)),
        },
        'ams' => {
            (map { 'e' . $_ => 1 } (0 .. 9)),
            (map { 'f' . $_ => 1 } (0 .. 9)),
        },
        'iva' => {
            (map { 'a' . $_ => 1 } (0 .. 9)),
            (map { 'b' . $_ => 1 } (0 .. 9)),
            (map { 'c' . $_ => 1 } (0 .. 9)),
            (map { 'd' . $_ => 1 } (0 .. 9)),
        },
    };
    return $etalon_blocks->{$dc};
}

sub _make_etalon_shards {
    my $shards_etalon = {};
    for (0 .. 49) {
        $shards_etalon->{sprintf("u%02d", $_)} = 'shard0';
        $shards_etalon->{sprintf("%02d",  $_)} = 'shard0';
    }
    for (0 .. 9) {
        $shards_etalon->{'a' . $_}  = 'shard0';
        $shards_etalon->{'aa' . $_} = 'shard0';
        $shards_etalon->{'b' . $_}  = 'shard0';
        $shards_etalon->{'ab' . $_} = 'shard0';
    }
    for (50 .. 99) {
        $shards_etalon->{sprintf("u%02d", $_)} = 'shard1';
        $shards_etalon->{sprintf("%02d",  $_)} = 'shard1';
    }
    for (0 .. 9) {
        $shards_etalon->{'c' . $_}  = 'shard1';
        $shards_etalon->{'ac' . $_} = 'shard1';
        $shards_etalon->{'d' . $_}  = 'shard1';
        $shards_etalon->{'ad' . $_} = 'shard1';
    }
    for (0 .. 9) {
        $shards_etalon->{'e' . $_}  = 'shard2';
        $shards_etalon->{'ae' . $_} = 'shard2';
    }
    for (0 .. 9) {
        $shards_etalon->{'f' . $_}  = 'shard3';
        $shards_etalon->{'af' . $_} = 'shard3';
    }
    return $shards_etalon;
}

sub _make_etalon_dc {
    my $dc_etalon = {
        'ams' => {
            'read' => {'ams' => 1,},
            'no_read'  => {},
            'write'    => {'ams' => 1,},
            'no_write' => {},
        },
        '*' => {
            'read'     => {},
            'no_read'  => {'ams' => 1,},
            'write'    => {},
            'no_write' => {'ams' => 1,},
        },
    };
    return $dc_etalon;
}
