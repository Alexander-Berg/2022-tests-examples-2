package MordaX::Block::Shortcuts::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Banners;
use MordaX::Block::Shortcuts;
use MordaX::Block::Shortcuts::Stack;
use MordaX::Options;
use MordaX::Req;

no  warnings 'experimental::smartmatch';

sub test_rearrange_shortcuts_pp : Test(12) {
    my ($self) = @_;

    my $shortcuts;
    for (qw(login weather taxi mail market_cart devices)) {
        $shortcuts->{$_} = {type => $_};
    }
    my $sc = $shortcuts;

    no warnings qw(redefine once);
    local *MordaX::Experiment::AB::flags = sub { MordaX::Experiment::AB::Flags::instance($_[0], 'MUTE_WARNINGS'); };

    my @tests;
    my ($in, $out, $desc);
    my $req = MordaX::Req->new();
    {
        no warnings qw(redefine);
        *Clid::instance = sub { bless({ client_partner => sub {} }, 'Clid') };
    }
    $req->{_BANNERS_} = MordaX::Banners->new($req, {solo => 1});

    {
        $in   = [@$sc{qw(weather taxi mail devices market_cart)}];
        $out  = [@$sc{qw(weather taxi mail devices market_cart)}];
        $desc = 'no market cart';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        local $shortcuts->{market}{bk_flag}    = 1;
        local $shortcuts->{market}{count}      = 1;
        $in   = [@$sc{qw(weather taxi mail devices market_cart)}];
        $out  = [@$sc{qw(weather taxi mail devices market_cart)}];
        $desc = 'no swap with market cart but w/o bk';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{market_cart}{bk_flag}    = 1;
        local $shortcuts->{market_cart}{count}      = 1;
        local *MordaX::Block::Shortcuts::shortcuts_settings = sub {
            return [{id => 'market_cart', swap_with_id => 'taxi'}];
        };
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        $in   = [@$sc{qw(weather taxi mail devices market_cart)}];
        $out  = [@$sc{qw(weather market_cart mail devices taxi)}];
        $desc = 'market with cart and bk';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{market_cart}{bk_flag}    = 1;
        local $shortcuts->{market_cart}{count}      = 1;
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        local *MordaX::Options::options = sub { 1 };
        $in   = [@$sc{qw(weather taxi mail devices market_cart)}];
        $out  = [@$sc{qw(weather taxi mail devices market_cart)}];
        $desc = 'no swap market with cart and bk but with disable option';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{market_cart}{bk_flag}    = 1;
        local $shortcuts->{market_cart}{count}      = 1;
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        $in   = [@$sc{qw(weather mail devices market_cart)}];
        $out  = [@$sc{qw(weather market_cart mail devices)}];
        $desc = 'market with cart and bk w/o taxi';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{login}{bk_flag}     = 1;
        local $shortcuts->{market_cart}{bk_flag}    = 1;
        local $shortcuts->{market_cart}{count}      = 1;
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        $in   = [@$sc{qw(login weather mail devices market_cart)}];
        $out  = [@$sc{qw(login weather market_cart mail devices)}];
        $desc = 'market with cart and bk w/o taxi with login on top';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{market_cart}{bk_flag}    = 1;
        local $shortcuts->{market_cart}{count}      = 1;
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        $in   = [@$sc{qw(mail devices market_cart)}];
        $out  = [@$sc{qw(market_cart mail devices)}];
        $desc = 'market with cart and bk w/o taxi w/o weather';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local *MordaX::Block::Shortcuts::get_shortcuts_orders = sub { {mail => 3} };
        $in   = [@$sc{qw(login weather taxi devices market_cart)}];
        $out  = [@$sc{qw(weather taxi login devices market_cart)}];
        $desc = 'no bk flag for login';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        $in   = [@$sc{qw(login weather taxi devices market_cart)}];
        $out  = [@$sc{qw(weather taxi devices market_cart login)}];
        $desc = 'no bk flag for login, no mail order';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{login}{bk_flag} = 1;
        local *MordaX::Block::Shortcuts::get_shortcuts_orders = sub { {mail => 3} };
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        $in   = [@$sc{qw(login weather taxi devices market_cart)}];
        $out  = [@$sc{qw(login weather taxi devices market_cart)}];
        $desc = 'bk flag for login';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{devices}{bk_flag} = 1;
        local $shortcuts->{devices}{bk_order} = 0;
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        $in   = [@$sc{qw(weather taxi devices market_cart)}];
        $out  = [@$sc{qw(devices weather taxi market_cart)}];
        $desc = 'bk order for devices, index 0';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }

    {
        no warnings qw(redefine);
        local $shortcuts->{devices}{bk_flag} = 1;
        local $shortcuts->{devices}{bk_order} = 5;
        local *MordaX::Banners::get_flag_show_url = sub { 1 };
        $in   = [@$sc{qw(weather taxi devices market_cart)}];
        $out  = [@$sc{qw(weather taxi market_cart devices)}];
        $desc = 'bk order for devices, index more than shortcuts length';

        $in = MordaX::Block::Shortcuts::rearrange_shortcuts_pp($req, $in);
        is_deeply($in, $out, $desc);
    }
}


use constant URL => 'div-stories://open?container_id=stack_shortcut&stories=';

sub test_stack_shortcut_get_deeplink : Test(3) {
    my $self = shift;

    my $req = {};
    $req->{stack_stories_hash} = {
        shortcut1 => [qw(st1 st2)],
        shortcut2 => [qw(st3 st4)],
        shortcut3 => [qw(st5 st6)],
        shortcut4 => [qw(st7 st8)],
    };
    my $stack_ids = [qw(shortcut1 shortcut2 shortcut3 shortcut4)];

    my $id = 'shortcut1';
    my $correct_url = URL . 'st1,st2;st3,st4;st5,st6;st7,st8;';
    my $url = MordaX::Block::Shortcuts::Stack::get_deeplink($req, $stack_ids, $id) // '';
    is($url, $correct_url);

    $id = 'shortcut2';
    $correct_url = URL . 'st3,st4;st5,st6;st7,st8;st1,st2;';
    $url = MordaX::Block::Shortcuts::Stack::get_deeplink($req, $stack_ids, $id) // '';
    is($url, $correct_url);

    $id = 'shortcut4';
    $correct_url = URL . 'st7,st8;st1,st2;st3,st4;st5,st6;';
    $url = MordaX::Block::Shortcuts::Stack::get_deeplink($req, $stack_ids, $id) // '';
    is($url, $correct_url);
}

1;
