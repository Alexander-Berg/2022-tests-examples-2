package MordaX::DivRendererHelper::Test;

use base qw(Test::Class);
use rules;

use JSON::XS;
use List::MoreUtils;
use MordaX::DivRendererHelper;
use MP::Logit;
use MordaX::Utils;
use Test::Most;

sub test_prepare_post_data : Test(1) {
    my $self = shift;

    my @test_cases = ({
        input_data => {
            block_A => {
                block_A_key1 => 'block_A_string_value',
                block_A_key2 => 42,
                block_A_key3 => [15, 11, 19, 92],
            },
        },
        expected_result => {
            homeparams => {
                scale_factor => 1,
            },
            block_A => {},
            blocks => {
                block_A => {
                    block_A_key1 => 'block_A_string_value',
                    block_A_key2 => 42,
                    block_A_key3 => [15, 11, 19, 92],
                }, 
            },
        },
        test_case_name => 'single block',
    });

    for (@test_cases) {
        my $actual_result = MordaX::DivRendererHelper::_prepare_post_data(undef, $_->{input_data});
        is_deeply($actual_result , $_->{expected_result}, $_->{test_case_name});
    }
}

sub test_get_div_data : Test(5) {
    my $self = shift;

    no warnings qw(redefine);

    local *MordaX::HTTP::new = sub {$self};
    {
        # Сетевой запрос не был создан.
        local *alias_exists = sub {
            return 0;
        };
        my $req_stub = MordaX::Req->new();
        ok(!MordaX::DivRendererHelper::instance($req_stub)->get_div_data($req_stub), 'no HTTP alias');
    }
    {
        # Авокадо вернул не 200 OK.
        local *alias_exists = sub {
            return 1;
        };
        local *result_req_info = sub {
            return {
                success => 0,
            }
        };
        my $req_stub = MordaX::Req->new();
        ok(!MordaX::DivRendererHelper::instance($req_stub)->get_div_data($req_stub), 'HTTP failure');
    }
    {
        # Авокадо вернул 200 OK, но вместо JSON-ки - что-то другое.
        local *alias_exists = sub {
            return 1;
        };
        local *result_req_info = sub {
            return {
                success => 1,
                response_content => 'some plain text',
            }
        };
        my $req_stub = MordaX::Req->new();
        # Ожидается, что будет предупреждение, что распарсить JSON'ку не удалось.
        local $SIG{__WARN__} = sub {};
        ok(!MordaX::DivRendererHelper::instance($req_stub)->get_div_data($req_stub), 'not JSON');
    }
    {
        # Авокадо вернул 200 OK, с нормальной JSON-кой, но с отсутствующими полями.
        local *alias_exists = sub {
            return 1;
        };
        local *result_req_info = sub {
            return {
                success => 1,
                response_content => JSON::XS->new()->utf8->encode({
                    div_templates => {
                        'template_one' => { 'template_one_key' => 'template_one_value' },
                        'template_two' => { 'template_two_key' => 'template_two_value' },
                    },
                }),
            }
        };
        my $req_stub = MordaX::Req->new();
        # my $result = MordaX::DivRendererHelper::instance($req_stub)->get_div_data($req_stub);
        ok(!MordaX::DivRendererHelper::instance($req_stub)->get_div_data($req_stub), 'no block field in JSON');
    }
    {
        # Авокадо вернул 200 OK и с валидной JSON-ниной.
        my $expected_result = {
                div_templates => {
                    'template_one' => { 'template_one_key' => 'template_one_value' },
                    'template_two' => { 'template_two_key' => 'template_two_value' },
                },
                div_jsons => {
                    'block_a' => {
                        'block_a_key' => 'block_a_value',
                    },
                    'block_b' => {
                        'block_b_key1' => 'block_b_value1',
                        'block_b_key2' => 'block_b_value2',
                    }
                }
            };

        # Авокадо вернул 200 OK, с нормальной JSON-кой, но с отсутствующими полями.
        local *alias_exists = sub {
            return 1;
        };
        local *result_req_info = sub {
            return {
                success => 1,
                response_content => JSON::XS->new()->utf8->encode({
                    block => [
                        {
                            id => 'block_a',
                            data => {
                                'block_a_key' => 'block_a_value',
                            },
                        },
                        {
                            id => 'block_b',
                            data => {
                                'block_b_key1' => 'block_b_value1',
                                'block_b_key2' => 'block_b_value2',
                            },
                        },
                    ],
                    div_templates => {
                        'template_one' => { 'template_one_key' => 'template_one_value' },
                        'template_two' => { 'template_two_key' => 'template_two_value' },
                    },
                }),
            }
        };
        my $req_stub = MordaX::Req->new();
        is_deeply(MordaX::DivRendererHelper::instance($req_stub)->get_div_data($req_stub), $expected_result, 'correct JSON');
    }
}

use constant TEST_YABS_FLAG => 'test_yabs_flag';
sub test_get_yabs_links : Test(5) {
    my $self = shift;

    my @test_cases = ({
        flags => {},
        expected_result => undef,
        test_case_name => 'no YABS flag',
    }, {
        flags => {
            flag_name => TEST_YABS_FLAG,
            urls => {
                click_url => '',
                show_url  => '',
            },
        },
        expected_result => undef,
        test_case_name => 'YABS flag exists, but URLs are empty',
    }, {
        flags => {
            flag_name => TEST_YABS_FLAG,
            urls => {
                click_url => 'https://yabs/click',
                show_url  => '',
            },
        },
        expected_result => {
            click_url => 'https://yabs/click',
        },
        test_case_name => 'only click URL',
    }, {
        flags => {
            flag_name => TEST_YABS_FLAG,
            urls => {
                click_url => '',
                show_url  => 'https://yabs/show',
            },
        },
        click_url_stub => '',
        show_url_stub  => 'https://yabs/show',
        expected_result => {
            show_url => 'https://yabs/show',
        },
        test_case_name => 'only show URL',
    }, {
        flags => {
            flag_name => TEST_YABS_FLAG,
            urls => {
                click_url => 'https://yabs/click',
                show_url  => 'https://yabs/show',
            },
        },
        expected_result => {
            click_url => 'https://yabs/click',
            show_url  => 'https://yabs/show',
        },
        test_case_name => 'both URLS',
    });

    no warnings qw(redefine);

    local *MordaX::RF::instance = sub {
        return $self;
    };

    my $real_logit = \&MordaX::DivRendererHelper::logit;
    local *MordaX::DivRendererHelper::logit = sub {
        if ($_[0] eq 'warning' && $_[1] =~ m/empty YABS urls/) {
            return;
        }
        goto &$real_logit;
    };

    for my $test_case (@test_cases) {
        my $req_stub = MordaX::Req->new();
        local *get_all_urls = sub {
            $test_case->{flags};
        };
        my $actual_result = MordaX::DivRendererHelper::_get_yabs_links($req_stub);
        is_deeply($actual_result, $test_case->{expected_result}, $test_case->{test_case_name});
    }
}

use constant TEST_REORDER_BLOCKS_RUNS => 5;
sub test_reorder_blocks : Test(17) { # : Test(TEST_REORDER_BLOCKS_RUNS * 3 + 2)
    my $self = shift;

    my @blocks_with_add = ('add1', 'add2');
    my @blocks_with_get = ('get1', 'get2');
    {
        # Берём исходный список блоков, тасуем их, переупорядоваичаем и проверяем, что перестановка работает как надо.
        my @origin_ids = ('A', 'B', 'C', MordaX::DivRendererHelper::HELPER_BLOCK_NAME, @blocks_with_add, @blocks_with_get);

        for my $offset (1 .. TEST_REORDER_BLOCKS_RUNS) {
            my $random_seed = 15_11_1992 + $offset;
            my $shuffled_ids = MordaX::Utils::shuffle_stable($random_seed, \@origin_ids);
            my $reordered_ids = MordaX::DivRendererHelper::_reorder_blocks(\@origin_ids, \@blocks_with_add, \@blocks_with_get);

            # Блоки с вызовом add должны располагаться сразу перед div_renderer_helper, а блоки с get - в самом конце.
            my $div_renderer_helper_index = List::MoreUtils::first_index { $_ eq MordaX::DivRendererHelper::HELPER_BLOCK_NAME } @$reordered_ids;
            ok($div_renderer_helper_index >= 0, "random seed = $random_seed - div_renderer_helper block exists");

            my @blocks_before_div_renderer_helper = @{$reordered_ids}[$div_renderer_helper_index-@blocks_with_add..$div_renderer_helper_index-1];
            my @blocks_at_the_end = @{$reordered_ids}[-@blocks_with_get..-1];

            is_deeply(\{sort @blocks_before_div_renderer_helper}, \{sort @blocks_with_add}, "random seed = $random_seed - blocks with add");
            is_deeply(\{sort @blocks_at_the_end}, \{sort @blocks_with_get}, "random seed = $random_seed - blocks with get");
        }
    }

    # Отдельно провеяем случай, когда блока div_renderer_helper нет в списке.
    {
        my @origin_ids_without_helper = ('A', 'B', 'C', @blocks_with_add, @blocks_with_get);
        my $reordered_ids = MordaX::DivRendererHelper::_reorder_blocks(\@origin_ids_without_helper, \@blocks_with_add, \@blocks_with_get);

        my $div_renderer_helper_index = List::MoreUtils::first_index { $_ eq MordaX::DivRendererHelper::HELPER_BLOCK_NAME } @$reordered_ids;
        ok($div_renderer_helper_index == -1, 'div_renderer_helper is absent - div_render_helper didn\'t appear after reorder');

        is_deeply(\@origin_ids_without_helper, $reordered_ids, 'div_renderer_is_absent - block order stayed the same');
    }
}

1;
