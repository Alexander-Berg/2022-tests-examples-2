# Тестовый блок для разработки в ноде
package MordaX::Block::Dev_test_block;
use rules;
use MP::Stopdebug;

use parent qw(MordaX::Block);

use DivCardV2::Builder;
use DivCardV2::JSBuilder;
use Handler::Api::Divcards;
use MordaX::Experiment::Filter;
use MordaX::Type;
use MP::Logit;
use MP::Utils;

sub is_block_enabled : Memoize_req {
    my ($req) = @_;
    return $req->{Getargshash}{dev_test_block} eq '1';
}

sub GetData {
    my ($this, $req, $page, $widgetsettings, %args) = @_;
    return unless is_block_enabled($req);
    my $p = {};

    $p->{show} = 1;

    # Данные для запроса div2 верстки в ноде
    my $divcards = Handler::Api::Divcards::instance($req);
    if ($p->{show} && _is_div2_by_js($req) && $divcards &&
        $divcards->allow_block_preprocessing($req, 'dev_test_block')
    ) {
        $divcards->add_prepared_data($req, 'dev_test_block', $p->{data});
    }

    $page->{ $this->TargetBlock() } = $p;
}

sub data_clean {
    my $this = shift;
    return $this->_convert_to_div_card(@_);
}

sub _is_div2_by_js {
    my ($req) = @_;
    return MordaX::Experiment::Filter::div2($req) && MordaX::Utils::is_option_turned_by_host($req, 'enable_div2_by_js');
}

sub _convert_to_div_card {
    my ($this, $req, $in, $args) = @_;

    if ( MordaX::Type::is_api_search_2($req) ) {
        return unless $in->{show};

        if (_is_div2_by_js($req)) {
            my $divcards = Handler::Api::Divcards::instance($req);
            if ($divcards && $divcards->allow_block_postprocessing($req, 'dev_test_block')) {
                return DivCardV2::JSBuilder::make_div_from_bulk($req, 'dev_test_block');
            }
            my $block = {
                id   => 'dev_test_block',
                data => $in->{data},
            };
            return DivCardV2::Builder::build($req, $block);
        }
    }

    return $in;
}

use Rapid::Base;
Rapid::Base::Rapid_package();
1;
