package MordaX::Experiment::AB::Flags::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::Experiment::AB::Flags;


sub test_add_browser_flag : Test(5) {
    my $self = shift;

    no warnings qw(redefine experimental::smartmatch);
    *add_browser_flag = \&MordaX::Experiment::AB::Flags::add_browser_flag;

    #
    # === $flag = {} && %args = ()
    #

    $self->{browser_flags} = {};
    my $flag = {};
    my %args = ();

    is_deeply(add_browser_flag($self, $flag, %args)->{browser_flags}, {}, '$flag = {} && %args = ()');

    #
    # === $flag = defined && %args = ()
    #

    $flag = {
        default_group_name => "group_name_disabled",
        name               => "exclusive_tab_opening_control",
        params             => {
            exclusive_tab_opening => {
                parents => 1,
                internals => 1,
            }
        }
    };

    is_deeply(add_browser_flag($self, $flag, %args)->{browser_flags}, {}, '$flag = defined && %args = ()');

    #
    # === $flag = {} && %args = defined
    #

    $flag = {};
    %args = (
        testid => 244994,
    );

    is_deeply(add_browser_flag($self, $flag, %args)->{browser_flags}, {}, '$flag = {} && %args = defined');

    #
    # === check schema
    #
   {
    $flag = {
        default_group_name => 'group_name_disabled',
        name               => 'exclusive_tab_opening_control',
        params             => {
            exclusive_tab_opening => {
                parents => 1,
                internals => 1,
            }
        }
    };
    my $result = {
        exclusive_tab_opening_control => {
            default_group_name => 'group_name_disabled',
            name               => 'exclusive_tab_opening_control',
            params             => {
                exclusive_tab_opening => {
                    internals => 1,
                    parents   => 1,
                }
            },
            testid             => 244994,
            salt               => '',
        }
    };

    is_deeply(add_browser_flag($self, $flag, %args)->{browser_flags}, $result, 'check schema');
   }

    $self->{browser_flags} = {
        exclusive_tab_opening_control => {
            default_group_name => 'group_name_disabled',
            name               => 'exclusive_tab_opening_control',
            testid             => 244994,
            salt               => '',
        }
    };

    $flag = {
            default_group_name => 'group_name_disabled',
            name               => 'exclusive_tab_opening_control_2',
    };
    add_browser_flag($self, $flag, %args);
    $flag = {
            default_group_name => 'group_name_disabled',
            name               => 'exclusive_tab_opening_control_3',
    };
    add_browser_flag($self, $flag, %args);

   {
    my $result = {
        exclusive_tab_opening_control => {
            default_group_name => 'group_name_disabled',
            name               => 'exclusive_tab_opening_control',
            testid             => 244994,
            salt               => '',
        },
        exclusive_tab_opening_control_2 => {
            default_group_name => 'group_name_disabled',
            name               => 'exclusive_tab_opening_control_2',
            testid             => 244994,
            salt               => '',
        },
        exclusive_tab_opening_control_3 => {
            default_group_name => 'group_name_disabled',
            name               => 'exclusive_tab_opening_control_3',
            testid             => 244994,
            salt               => '',
        }
    };

    is_deeply($self->{browser_flags}, $result, 'several flags');
   }
}

1;
