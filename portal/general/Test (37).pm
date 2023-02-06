package MordaX::Block::Bottom_sheet_div::Test;

use base qw(Test::Class);

use MordaX::Block::Bottom_sheet_div;
use MordaX::Options;
use MordaX::Req;
use MP::Logit;
use rules;
use Test::Most;

no warnings qw(experimental::smartmatch redefine);

sub test_get_tools_enabled_features : Test(1) {
    my $self = shift;

    my $req = {
        all_postargs => {
            features => '[
              {
                "enabled": false,
                "feature": "ya_plus"
              },
              {
                "enabled": true,
                "feature": "aon"
              },
              {
                "enabled": true,
                "feature": "disk"
              },
              {
                "enabled": false,
                "feature": "keyboard"
              }
            ]',
        }
    };

    local *MordaX::Data_get::get_static_data = sub {
        return [
            {id => 'keyboard', feature_id => 'keyboard'},
            {id => 'whocalls', feature_id => 'aon'},
            {id => 'disk'},
        ];
    };

    my $expected = ['whocalls'];
    my $got = MordaX::Block::Bottom_sheet_div::get_tools_enabled_features($req);

    is_deeply($expected, $got);
}

sub test_get_list_services_tools : Test(1) {
    my $self = shift;

    my $section_data = {
        list_services => 'covid_qr gibdd whocalls keyboard vision quasar my_books bonuscards videoeditor',
    };
    my $req = {
        Getargshash => {
            recents => 'quasar,vision,whocalls,gibdd',
        },
    };
    local *MordaX::Block::Bottom_sheet_div::get_tools_enabled_features = sub {
        return ['whocalls', 'keyboard'];
    };
    local *MordaX::Block::Bottom_sheet_div::get_tools_new_services = sub {
        return ['bonuscards', 'keyboard', 'gibdd', 'videoeditor'];
    };

    my $expected = ['bonuscards', 'videoeditor', 'quasar', 'vision', 'gibdd', 'covid_qr', 'my_books', 'whocalls', 'keyboard'];
    my $got = MordaX::Block::Bottom_sheet_div::get_list_services_tools($req, $section_data);

    is_deeply($expected, $got);
}

1;
