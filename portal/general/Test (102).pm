package MordaX::Layout::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Layout;
use MordaX::Layout::Touch;

use constant TEST_BLOCK_TYPE => 'X';

sub creation : Tests {
    my $layout = MordaX::Layout->new();
    isa_ok($layout, 'MordaX::Layout');
    # creation with req
    $layout = MordaX::Layout->new(req => {});
    is($layout, undef, "can't detect morda type, return undef");
    # req => class
    my @tests = (
        [{ api_search   => 1 }       => 'MordaX::Layout::APIv1'],
        [{ api_search   => 2 }       => 'MordaX::Layout::APIv2'],
        [{ MordaContent => 'touch' } => 'MordaX::Layout::Touch'],
    );
    for (@tests) {
        my ($req, $class) = @$_;
        $layout = MordaX::Layout->new(req => $req);
        isa_ok($layout, 'MordaX::Layout');
        isa_ok($layout, $class);
    }
};

sub layout : Tests {
    my @items    = qw(a b c d e f);
    my $layout   = MordaX::Layout->new(items => [@items]);
    my $expected = \@items;
    my $got      = $layout->layout();
    is_deeply($got, $expected);
};

sub add : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c)]);
    my $ret = $layout->add('d');
    is_deeply($layout->layout(), [qw(a b c d)], 'add with undef index');
    is($ret, $layout, 'add returns same object');
    $layout->add('0', 0);
    is_deeply($layout->layout(), [qw(0 a b c d)], 'add with zero index');
    $layout->add('aa', 2)->add('bb', 4);
    is_deeply($layout->layout(), [qw(0 a aa b bb c d)], 'add different index');
};

sub del : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $ret = $layout->del(0);
    is_deeply($layout->layout(), [qw(b c d e)], 'del zero index');
    is($ret, $layout, 'del returns same object');
    $layout->del(2)->del(1);
    is_deeply($layout->layout(), [qw(b e)], 'del different index');
};

sub swap : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $ret = $layout->swap(0, 2);
    is_deeply($layout->layout(), [qw(c b a d e)], 'swap');
    is($ret, $layout, 'swap returns same object');
};

sub move : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $ret = $layout->move(3, 0);
    is_deeply($layout->layout(), [qw(d a b c e)], 'to < from');
    is($ret, $layout, 'move returns same object');
    $layout->move(3, 3);
    is_deeply($layout->layout(), [qw(d a b c e)], 'to == from');
    $layout->move(0, 3);
    is_deeply($layout->layout(), [qw(a b c d e)], 'to > from');
    $layout->move(2, 1);
    is_deeply($layout->layout(), [qw(a c b d e)], 'to < from');
    $layout->move(0, 0);
    is_deeply($layout->layout(), [qw(a c b d e)], 'to == from');
    $layout->move(1, 3);
    is_deeply($layout->layout(), [qw(a b d c e)], 'to > from');
    $layout->move(2, 4);
    is_deeply($layout->layout(), [qw(a b c e d)], 'to - last index');
    $layout->move(2, 0);
    is_deeply($layout->layout(), [qw(c a b e d)], 'to - first index');
};

sub move_relative : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b x c d e)]);
    my $ret = $layout->move_relative('x' => 'a');
    is_deeply($layout->layout(), [qw(x a b c d e)], 'x => a');
    is($ret, $layout, 'move_relative returns same object');
    $layout->move_relative('cx' => 'a');
    is_deeply($layout->layout(), [qw(x a b c d e)], 'unknown id');
    $layout->move_relative('x' => 'x');
    is_deeply($layout->layout(), [qw(x a b c d e)], 'move to same position');
    $layout->move_relative('x');
    is_deeply($layout->layout(), [qw(x a b c d e)], 'empty to');
    $layout->move_relative('x' => qw(d a h x z b));
    is_deeply($layout->layout(), [qw(a b c d x e)], 'x => qw(d a h x z b)');
};

sub move_under : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $ret = $layout->move_under('b', 'd');
    is_deeply($layout->layout(), [qw(a c d b e)], 'to > from');
    is($ret, $layout, 'move_under returns same object');
    $ret = $layout->move_under('b', 'b');
    is_deeply($layout->layout(), [qw(a c d b e)], 'to == from');
    $ret = $layout->move_under('b', 'a');
    is_deeply($layout->layout(), [qw(a b c d e)], 'to < from');
    $ret = $layout->move_under('b', 'y');
    is_deeply($layout->layout(), [qw(a b c d e)], 'bad id');
    $ret = $layout->move_under('a', 'b', 2);
    is_deeply($layout->layout(), [qw(b c d a e)], 'with offset');
    $ret = $layout->move_under('a', 'd', 2);
    is_deeply($layout->layout(), [qw(b c d e a)], 'offset out of bounds');
    $ret = $layout->move_under('a', 'e', 1);
    is_deeply($layout->layout(), [qw(b c d e a)], 'nothing changed');
    $ret = $layout->move_under('b', 'd', 1);
    is_deeply($layout->layout(), [qw(c d e b a)], 'to - offset > from');
};

sub position_to_index : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my @tests = (
        [undef, undef],
        [-7,    0],
        [-6,    0],
        [-5,    0],
        [-4,    1],
        [-3,    2],
        [-2,    3],
        [-1,    4],
        [0,     0],
        [1,     0],
        [2,     1],
        [3,     2],
        [4,     3],
        [5,     4],
        [6,     4],
        [7,     4],
    );
    for (@tests) {
        my ($pos, $index) = @$_;
        is(
            $layout->position_to_index($pos),
            $index,
            join('=>', map { $_ // 'undef' } ($pos, $index))
        );
    }
};

sub iexists : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c)]);
    ok($layout->iexists(0));
    ok($layout->iexists(1));
    ok($layout->iexists(2));
    ok(not $layout->iexists(3));
};

sub search : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    is($layout->search('b'), 1);
    is($layout->search('b', 2), undef);
    is($layout->search('z'), undef);
};

sub rsearch : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a c e b f)]);
    is($layout->rsearch('b'), 3);
    is($layout->rsearch('b', 2), undef);
    is($layout->search('z'), undef);
};

sub del_by_item : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $ret = $layout->del_by_item('b');
    is_deeply($layout->layout(), [qw(a c d e)], 'del_by_item a');
    is($ret, $layout, 'del_by_item returns same object');
    $layout->del_by_item('z');
    is_deeply($layout->layout(), [qw(a c d e)], 'try to del unknown item');
};

sub clean_by_hash : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $ret = $layout->clean_by_hash({ b => 1, d => 1, x => 1 });
    is_deeply($layout->layout(), [qw(b d)], 'clean_by_hash');
    is($ret, $layout, 'clean_by_hash returns same object');
};

sub as_hash : Tests {
    my $layout = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $got = $layout->as_hash();
    my $expected = {
        a => { index => 0, item => 'a' },
        b => { index => 1, item => 'b' },
        c => { index => 2, item => 'c' },
        d => { index => 3, item => 'd' },
        e => { index => 4, item => 'e' },
    };
    is_deeply($got, $expected, 'as_hash');
};

sub sort_by_array : Tests {
    my $layout     = MordaX::Layout->new(items => [qw(a b c d e)]);
    my $sort_array = [qw(z c e b x y)];
    my $expected   = [qw(c e b a d)];
    my $ret        = $layout->sort_by_array($sort_array);
    is_deeply($layout->layout(), $expected, 'sort_by_array');
    is($ret, $layout, 'sort_by_array returns same object');
    # layout now qw(c e b a d)
    $layout->disable_shuffle('b')->disable_shuffle('a');

    no warnings qw(redefine);
    local *MordaX::Layout::logit = sub {};

    $ret = $layout->sort_by_array([qw(a b c)], check_shuffle => 1);
    is($ret, $layout, 'sort_by_array with check_shuffle returns same object');
    is_deeply($layout->layout(), $expected, 'check_shuffle in sort array');
    $ret = $layout->sort_by_array([qw(a b c e d)], check_shuffle => 1, strict => 1);
    ok(!$ret, 'strict mode with check_shuffle');
    $ret = $layout->sort_by_array([qw(a a a a a)], strict => 1);
    ok(!$ret, 'strict mode with dups');
    {
        no warnings qw(redefine);

        local *MordaX::Layout::dmp = sub { };
        $ret = $layout->sort_by_array([qw(a)], strict => 1);
        ok(!$ret, 'strict mode not enough items');
        $ret = $layout->sort_by_array([qw(a b c d e f)], strict => 1);
        ok(!$ret, 'strict mode too many items');
    }
    $ret = $layout->sort_by_array([qw(a b s d e)], strict => 1);
    ok(!$ret, 'strict mode unknown elements');
    is_deeply($layout->layout(), $expected, 'all failed sorts with strict mode didn\'t change layout');
    $ret = $layout->sort_by_array([qw(a b c d e)], strict => 1);
    is($ret, $layout, 'strict mode without shuffle_checks');
    $expected = [qw(a b c d e)];
    is_deeply($layout->layout(), $expected, 'strict mode without shuffle_checks');
};

sub deduplication : Tests {
    no warnings qw(redefine);

    local *MordaX::Layout::logit = sub { };
    my $layout = MordaX::Layout->new(items => [qw(a b c a b d e d e)]);
    is_deeply($layout->layout(), [qw(a b c d e)], 'deduplicate on creation');
    $layout->add('a');
    is_deeply($layout->layout(), [qw(a b c d e)], 'deduplicate on add');
    $layout->del(0);
    $layout->add('a');
    $layout->add('a');
    $layout->add('a');
    is_deeply($layout->layout(), [qw(b c d e a)], 'after del');
    $layout->clean_by_hash({ c => 1 });
    $layout->add('a');
    $layout->add('a');
    $layout->add('a');
    is_deeply($layout->layout(), [qw(c a)], 'after clean_by_hash');
};

sub APIv1 : Tests {
    my $layout = MordaX::Layout->new(req => { api_search => 1 });
    my $items = $layout->layout();
    $layout->add(1,2,3,4,5);
    $layout->del(2);
    $layout->move(3,5);
    $layout->swap(2,5);
    is_deeply($layout->layout(), $items, 'For APIv1 layout has not been changed');
};

sub APIv2 : Tests {
    my $layout = MordaX::Layout->new(req => { api_search => 2 });
    my @items = (
        { id => 'a' },
        { id => 'b', type => 'x' },
        {},
        undef,
        { id => 'c', heavy => 'some true' },
    );
    $layout->add($_) for @items;
    my $expected = [
        { id => 'a', type => 'a', heavy => 0 },
        { id => 'b', type => 'x', heavy => 0 },
        { id => 'c', type => 'c', heavy => 1 },
    ];
    my $expected_as_hash = {
        a => { index => 0, item => { id => 'a', type => 'a', heavy => 0 } },
        b => { index => 1, item => { id => 'b', type => 'x', heavy => 0 } },
        c => { index => 2, item => { id => 'c', type => 'c', heavy => 1 } },
    };
    is_deeply($layout->layout(), $expected, 'add test');
    is($layout->search('b'), 1, 'search test');
    is_deeply($layout->as_hash(), $expected_as_hash, 'as_hash');
    $expected = [
        { id => 'b', type => 'x', heavy => 0 },
        { id => 'c', type => 'c', heavy => 1 },
    ];
    $layout->clean_by_hash({ b => 1, c => 1 });
    is_deeply($layout->layout(), $expected, 'clean_by_hash');
    $expected = [
        { id => 'c', type => 'c', heavy => 1 },
        { id => 'b', type => 'x', heavy => 0 },
    ];

    # FIXME: временное решение сортирвоки в пп
    #$layout->sort_by_array([qw(a x c d)]);
    #is_deeply($layout->layout(), $expected, 'sort_by_array');
    $layout = MordaX::Layout->new(req => { api_search => 2 });
    $layout->add($_) for @$expected;
    # END FIXME

    is($layout->search('b'), 1, 'search');
    $expected = [
        { id => 'b', type => 'x', heavy => 0 },
    ];
    $layout->del_by_item('c');
    is_deeply($layout->layout(), $expected, 'del_by_item');
    $layout = MordaX::Layout->new(req => { api_search => 2 });
    $layout->add({id => 'search'})
        ->add({id => 'now'})
        ->add({id => 'assist'})
        ->add({id => 'div_1', type => 'div'})
        ->add({id => 'div_2', type => 'div'})
        ->add({id => 'div_3', type => 'div'})
        ->add({id => 'topnews'})
        ->add({id => 'weather'})
        ->add({id => 'zen'});
    is($layout->position_to_index(1), 6, 'position_to_index with offset: 1 => 6');
    is($layout->position_to_index(2), 7, 'position_to_index with offset: 2 => 7');
    is($layout->position_to_index(3), 8, 'position_to_index with offset: 3 => 8');
    is($layout->position_to_index(30), 8, 'position_to_index with offset: 30 => 8');
    is($layout->position_to_index(-1), 8, 'position_to_index with offset: -1 => 8');
    is($layout->position_to_index(-2), 7, 'position_to_index with offset: -2 => 7');
    is($layout->position_to_index(-3), 6, 'position_to_index with offset: -3 => 6');
    is($layout->position_to_index(-4), 6, 'position_to_index with offset: -4 => 6');
    is($layout->position_to_index(-30), 6, 'position_to_index with offset: -30 => 6');
};

sub filter_blocks_by_div_feature : Tests {
    my $layout = MordaX::Layout->new();
    my $items = [
        {id => 'block1'},
        {id => 'div_block2'},
        {id => 'block3'},
        {id => 'block2'},
        {id => 'div_block4'}
    ];
    my $correct_result = [
        {id => 'block1'},
        {id => 'div_block2'},
        {id => 'block3'},
        {id => 'div_block4'}
    ];

    is_deeply($layout->filter_blocks_by_div_feature($items), $items, 'option doesn\'t enabled');

    no warnings qw(redefine);
    local *MordaX::Utils::options = sub { return 1; };

    is_deeply($layout->filter_blocks_by_div_feature($items), $correct_result, 'correct filtration');
};

sub reorder_blocks_after_processing : Tests {
    my @tests = (
        { ids => [qw/A5 A3 A1 A2 A4/],                             argument => [qw/A1 A2 A3 A4 A5/],                             expected => [qw/A1 A2 A3 A4 A5/],                             test_case_name => 'reorder all blocks'},
        { ids => [qw/A5 A3 A1 A2 A4/],                             argument => [qw/A1 A2 A3 A4 A5 A6 A7/],                       expected => [qw/A1 A2 A3 A4 A5/],                             test_case_name => 'reorder non-existent blocks'},
        { ids => [qw/A5 A3 A1 A2 A4/],                             argument => [qw/A4 A5/],                                      expected => [qw/A4 A3 A1 A2 A5/],                             test_case_name => 'reorder partially'},
        { ids => [qw/A5 A3 A1 A2 A4 Z1 Z2 Z3/],                    argument => [qw/A1 A2 A3 A4 A5/],                             expected => [qw/A1 A2 A3 A4 A5 Z1 Z2 Z3/],                    test_case_name => 'reorder only A-blocks'},
        { ids => [qw/A5 A3 A1 A2 A4/],                             argument => [qw/A4/],                                         expected => [qw/A5 A3 A1 A2 A4/],                             test_case_name => 'single block'},
        { ids => [qw/A5 A3 A1 A2 A4/],                             argument => [qw//],                                           expected => [qw/A5 A3 A1 A2 A4/],                             test_case_name => 'no blocks'},
        { ids => [qw/A13 A9 A10 A7 A12 A6 A1 A8 A2 A3 A11 A5 A4/], argument => [qw/A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 A13/], expected => [qw/A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 A13/], test_case_name => 'really long layout'},
    );
    for my $test (@tests) {
        my $layout = MordaX::Layout->new(req => { api_search => 2 });
        $layout->add({ id => $_, type => TEST_BLOCK_TYPE, heavy => 0}) for @{$test->{ids}};
        $layout->reorder_blocks_after_processing($test->{argument});
        is_deeply($layout->layout(), [map {{id => $_, type => TEST_BLOCK_TYPE, heavy => 0}} @{$test->{expected}}], $test->{test_case_name});
    }
};

sub test_rearrange_touch_blocks : Tests {
    my ($self) = @_;

    my ($in, $out, $desc);

    my $req = MordaX::Req->new();
    $req->{MordaContent} = 'touch';

    my $layout = MordaX::Layout->new(req => $req);

    no warnings qw(redefine);

    {
        $desc = 'rates folded';

        $in   = [qw(covid_gallery rates news)];
        $out  = [qw(news rates covid_gallery)];
        $layout->{items} = $in;

        MordaX::Layout::Touch::rearrange_touch_blocks($layout, $req);
        is_deeply($layout->{items}, $out, $desc);
    }

    {
        $desc = 'rates unfolded';

        $in   = [qw(news covid_gallery rates)];
        $out  = [qw(news covid_gallery rates)];
        $layout->{items} = $in;

        local $req->{YCookies} = MordaX::YCookie->new($req);
        $req->{YCookies}->setyp(stst => 'full');

        MordaX::Layout::Touch::rearrange_touch_blocks($layout, $req);
        is_deeply($layout->{items}, $out, $desc);
    }

    {
        $desc = 'rates with option';

        $in   = [qw(covid_gallery rates news)];
        $out  = [qw(covid_gallery rates news)];
        $layout->{items} = $in;

        local *MordaX::Options::options = sub {
            return 1 if ($_[0] eq 'disable_rates_under_news');
        };

        MordaX::Layout::Touch::rearrange_touch_blocks($layout, $req);
        is_deeply($layout->{items}, $out, $desc);
    }
}

1;
