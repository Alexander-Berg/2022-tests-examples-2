package Handler::Api::DivFullscreens::Test;

use Test::Most;
use base qw(Test::Class);

use Handler::Api::DivFullscreens;
use rules;
use MP::Logit;

no  warnings 'experimental::smartmatch';

sub test_get_fullscreen : Test(1) {
    my ($self) = @_;
    local *Handler::Api::DivFullscreens::is_enabled = sub { 1 };

    local *MordaX::Data_get::get_static_data = sub {{
        id => 'fs',
        template => 'tfs',
        data => '{"key": "value", "arr": [{}]}',
    }};

    my $expected = {
        id => 'fs',
        template => 'tfs',
        key => "value",
        arr => [{}],
    };

    my $got = Handler::Api::DivFullscreens::get_fullscreen({}, 'fs');

    is_deeply($expected, $got);
}

sub test_add : Test(2) {
    my ($self) = @_;
    local *Handler::Api::DivFullscreens::is_enabled = sub { 1 };

    my $fs_items = [
        {id => 'fs2', template => 'tfs2'},
        {id => 'fs3', template => 'tfs3', key => 'value'},
    ];

    my $status_expected = [1, 1];
    my $div_fs_storage_expected = {
        fs2 => { id => 'fs2', template => 'tfs2' },
        fs3 => { id => 'fs3', key => 'value', template => 'tfs3' }
    };

    my $req = {};
    my $status_got = [ map { Handler::Api::DivFullscreens::add($req, $_) } @$fs_items ];

    is_deeply($status_expected, $status_got);
    is_deeply($div_fs_storage_expected, $req->{div_fs_storage});
}

sub test_make_blocks : Test(1) {
    my ($self) = @_;

    my $div = {
        api_search_redefine_type => 'div2',
        corner_radius => 24,
        disabled_by_default => 1,
        log_id => 'div_fullscreens',
        fullscreens => [
            {
                data => {
                    log_id => 'div_fs_1',
                    states => []
                },
                id => 'div_fs_1',
                utime => 1638534245
            },
            {
                data => {
                    log_id => 'div_fs_2',
                    states => [{}]
                },
                id => 'div_fs_2',
                utime => 1638534246
            }
        ],
        show => 1,
        ttl => 900,
        ttv => 1200
    };

    my $expected = [
        {
            type => 'div2',
            corner_radius => 24,
            disabled_by_default => 1,
            data => {
                log_id => 'div_fs_1',
                states => []
            },
            id => 'div_fs_1',
            utime => 1638534245,
            ttl => 900,
            ttv => 1200,
        },
        {
            type => 'div2',
            corner_radius => 24,
            disabled_by_default => 1,
            data => {
                log_id => 'div_fs_2',
                states => [{}]
            },
            id => 'div_fs_2',
            utime => 1638534246,
            ttl => 900,
            ttv => 1200,
        },
    ];

    my $got = Handler::Api::DivFullscreens::_make_blocks($div);

    is_deeply($expected, $got);
}

1;
