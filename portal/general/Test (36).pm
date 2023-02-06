package MordaX::Block::Bottom_sheet_api::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::Block::Bottom_sheet_api;

sub _startup : Test(startup) {
    my $self = shift;

}

sub _setup : Test(setup) {
    my $self = shift;

}

sub test_get_all_services : Test(2) {
    my $self = shift;

    *get_all_services = \&MordaX::Block::Bottom_sheet_api::get_all_services;

    no warnings qw(redefine experimental::smartmatch);
    local *MordaX::Block::Services::select = sub {
        [
    		{
        		all_group => 'searchBlock',
        		id        => 'taxi',
   			}
		]
    };

	my $expected = {
		taxi => {
			all_group => 'searchBlock',
			id => 'taxi',
			tanker_name => 'allServices.searchBlock.taxi.title',
		}
	};
	is_deeply(get_all_services({}), $expected, 'test message');

    local *MordaX::Utils::options = sub {
        if ($_[0] eq 'new_bs_apps_export') {
            return 1;
        }
        return 0;
    };

    local *MordaX::Data_get::get_static_data = sub {
        [];
    };

	is_deeply(get_all_services({}), $expected);

}



1;
