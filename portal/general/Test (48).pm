package MordaX::Block::Verticals::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use MordaX::Req;
use base qw(Test::Class);

use MordaX::Block::Verticals;

sub setup : Test(setup) {
    my $self = shift;

    $self->{req} = MordaX::Req->new();
}

sub test__get_less_zen_yabro_title : Test(8) {
    my $self = shift;

    no warnings qw(redefine);
    *get_less_zen_yabro_title = \&MordaX::Block::Verticals::get_less_zen_yabro_title;

    my $row = {
        id => 'topnews',
    };
    is(get_less_zen_yabro_title($self->{req}, $row), undef, 'id => topnews');


    $row->{id} = 'zen';
    is(get_less_zen_yabro_title($self->{req}, $row), undef, 'less_zen => undef');


    $self->{req}{Getargshash}{less_zen} = 1;
    is(get_less_zen_yabro_title($self->{req}, $row), undef, 'less_zen_title => undef');


    local *MordaX::Options::options = sub {
        if ($_[0] eq 'disable_less_zen_title') {
            return 1;
        }
        return;
    };
    $row->{less_zen_title} = 'zen.tanker.less_zen_title';
    is(get_less_zen_yabro_title($self->{req}, $row), undef, 'options disable_less_zen_title => 1');


    local *MordaX::Options::options = sub {
        if ($_[0] eq 'disable_less_zen_title') {
            return 0;
        }
        return;
    };
    my $error_type;
    my $error_msg;
    local *MordaX::Block::Verticals::logit = sub {
        $error_type = $_[0];
        $error_msg  = $_[1];
    };
    is(get_less_zen_yabro_title($self->{req}, $row), undef, 'disable_less_zen_title => 1');


    is($error_type, 'nodata', 'logit error_type => nodata');


    is($error_msg, "No less_zen_title=('zen.tanker.less_zen_title') in tanker for zen page 'zen'", 'logit error_msg => no less_zen_title ..');


    local *MordaX::Block::Verticals::lang = sub {
        return 'Title';
    };
    is(get_less_zen_yabro_title($self->{req}, $row), 'Title', 'less_zen_title => Title');
}

sub test__get_yabro_title : Test(4) {
    my $self = shift;

    no warnings qw(redefine);
    *get_yabro_title = \&MordaX::Block::Verticals::get_yabro_title;

    my $custom_lang;
    my $row = 'abc';
    is(get_yabro_title($self->{req}, $row, $custom_lang), undef, '$row is string');


    $row = { title => 'Main' };
    is(get_yabro_title($self->{req}, $row, $custom_lang), undef, '$row->{title} = Main');


    local *MordaX::Block::Verticals::lang = sub {
        return 'Title';
    };
    is(get_yabro_title($self->{req}, $row, $custom_lang), 'Title', 'lang = Title');


    local *MordaX::Block::Verticals::get_less_zen_yabro_title = sub {
        return 'Zen';
    };
    is(get_yabro_title($self->{req}, $row, $custom_lang), 'Zen', 'get_less_zen_yabro_title = Zen');
}

1;
