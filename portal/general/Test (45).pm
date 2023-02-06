package MordaX::Block::Topnews::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::Block::Topnews;

sub _redefine_object : Test(startup) {
}

sub make_fixture : Test(setup) {
    my $self = shift;
}

sub test_get_image_resize : Test(5) {
    my $self = shift;

    my @data = (
        {
            options => [],
            type    => ['is_fast_api_widget_2'],
            result  => 'large'
        },
        {
            options => [],
            type    => ['is_fast_api_widget_2', 'is_api_android_widget_old'],
            result  => '100x100'
        },
        {
            options => [],
            type    => [],
            result  => undef,
        },
        {
            options => [],
            type    => ['is_tv'],
            result  => '380x214'
        },
        {
            options => [],
            type    => ['is_api_launcher'],
            result  => '100x100'
        },
    );

    *get_image_resize = \&MordaX::Block::Topnews::get_image_resize;

    for my $test (@data) {
        no warnings qw(redefine experimental::smartmatch);
        local *MordaX::Type::is_fast_api_widget_2 = sub {
            if ('is_fast_api_widget_2' ~~ $test->{type}) {
                return 1;
            }

            return 0;
        };
        local *MordaX::Type::is_api_android_widget_old = sub {
            if ('is_api_android_widget_old' ~~ $test->{type}) {
                return 1;
            }

            return 0;
        };
        local *MordaX::Type::is_tv = sub {
            if ('is_tv' ~~ $test->{type}) {
                return 1;
            }

            return 0;
        };
        local *MordaX::Type::is_api_launcher = sub {
            if ('is_api_launcher' ~~ $test->{type}) {
                return 1;
            }

            return 0;
        };
        local *MordaX::Utils::options = sub {
            my $option = shift;
            if ($option ~~ $test->{options}) {
                return 1;
            }

            return 0;
        };


        is(get_image_resize(), $test->{result});
    }
}

sub test_getdata_divjson : Test(10) {
    my $self = shift;

    my @valid_jsons = (
        {
            input_json => {
                div_templates => {
                    "template_key" => "template_value",
                },
                block => [{
                    data => {
                        "block_data_key_A" => "block_data_value_A",
                        "block_data_key_B" => "block_data_value_B",
                    },
                }],
                ttv => 1200,
                ttl => 300,
            },
            expected_page => {
                show => 1,
                api_search_external_div_templates => {
                    "template_key" => "template_value"
                },
                api_search_redefine_type => "div2",
                block_data_key_A => "block_data_value_A",
                block_data_key_B => "block_data_value_B",
                ttv => 1200,
                ttl => 300,
            },
            test_case_name => "valid JSON",
        },
        {
            input_json => {
                div_templates => {
                },
                block => [{
                    data => {
                        "block_data_key_A" => "block_data_value_A",
                        "block_data_key_B" => "block_data_value_B",
                    },
                }],
                ttv => 1200,
                ttl => 300,
            },
            expected_page => {
                show => 1,
                api_search_external_div_templates => {
                },
                api_search_redefine_type => "div2",
                block_data_key_A => "block_data_value_A",
                block_data_key_B => "block_data_value_B",
                ttv => 1200,
                ttl => 300,
            },
            test_case_name => "valid JSON without external templates",
        },
    );

    my @corrupted_jsons = (
        {
            input_json => {},
            test_case_name => "empty JSON",
        },
        {
            input_json => {
                div_templates => {
                    "template_key" => "template_value",
                },
                block => [{

                }],
            },
            test_case_name => "no data",
        },
        {
            input_json => {
                block => [{
                    data => {
                        "block_data_key_A" => "block_data_value_A",
                        "block_data_key_B" => "block_data_value_B",
                    },
                }],
                ttv => 1200,
                ttl => 300,
            },
            test_case_name => "no templates",
        },
        {
            input_json => {
                div_templates => {
                    "template_key" => "template_value",
                },
                block => [],
            },
            test_case_name => "no blocks",
        },
        {
            input_json => {
                div_templates => {
                    "template_key" => "template_value",
                },
                block => [{
                    data => {
                        "block1_key" => "block1_data",
                    },
                }, {
                    data => {
                        "block2_key" => "block2_data",
                    }
                }],
            },
            test_case_name => "more than one block",
        },
        {
            input_json => {
                div_templates => {
                    "template_key" => "template_value",
                },
                block => {},
            },
            test_case_name => "block field is not an array",
        },
    );

    no warnings qw(redefine);

    local *TargetBlock = sub {
         return "topnews_test";
    };

    local *get_data_divjson = sub {
        my ($self, $json) = @_;
        
        local *MordaX::HTTP::result_req_info = sub {
            return {
                response_content => JSON::XS::encode_json($json),
                response_headers => $self,
                success          => 1,
            };
        };

        local *header = sub {};

        local *MordaX::HTTP::alias_exists = sub {
            return 1;
        };

        $self->{page} = {};
        return MordaX::Block::Topnews::GetData_divjson($self, {}, $self->{page}, {});
    };

    for (@valid_jsons) {
        is(get_data_divjson($self, $_->{input_json}), 1, $_->{test_case_name} . ' - check return value');
        is_deeply($self->{page}->{$self->TargetBlock()}, $_->{expected_page}, $_->{test_case_name} . ' - check page data');
    }

    for (@corrupted_jsons) {
        is_deeply(get_data_divjson($self, $_->{input_json}), 0, $_->{test_case_name});
    }
}

1;
