package DivCard::TestInfoCard;

# WARNING: TestingInstance only. Карточка для дебаг информации при показе всех
#          дивов.

use rules;
use MP::Stopdebug;

use MP::Logit qw(dmp logit);
use MP::Utils;

use base qw(DivCard::Base::Card);

use DivCard::Base::Constants;
use DivCard::Base::Block::Table;

use MordaX::Config;

sub process { $MordaX::Config::TestingInstance ? shift->next::method(@_) : undef }

sub get_subs_data {
    my $self  = shift;
    my $guard = $self->scope_errors();
    $self->quiet_on_warning(1);
    return $self->next::method(@_);
}

sub make {
    my ($self, $req, $card) = @_;

    my $data = $card->{'data'};

    $self->die_on_error(1);
    $self->add_background_solid(color => $data->{'bgcolor'});
    $self->add_state(id => 1);

    $self->add_block_separator(size => DC_SIZE_XS);
    $self->add_block_universal(
        title      => $data->{'title'},
        title_color      => $data->{'title_color'},
        text       => $data->{'text'},
        font_color => $data->{'color'},
    );
    $self->add_block_separator(size => DC_SIZE_XS);

    if (is_array_size (my $debug = $data->{'debug'})) {
        my $table = DivCard::Base::Block::Table->new();
        $table->add_column()->add_column()->add_column()->add_column();
        my $head = $table->add_row();
        $head->add_text_cell(text => 'class', halign => DC_HALIGN_CENTER);
        $head->add_text_cell(text => 'status', halign => DC_HALIGN_CENTER);
        $head->add_text_cell(text => 'us', halign => DC_HALIGN_CENTER);
        $head->add_text_cell(text => 'kb', halign => DC_HALIGN_CENTER);

        for my $d (@$debug) {
            my $row = $table->add_row();
            $row->add_text_cell(text => $d->[0], halign => DC_HALIGN_LEFT);
            $row->add_text_cell(text => $d->[1], halign => DC_HALIGN_CENTER);
            $row->add_text_cell(text => $d->[2], halign => DC_HALIGN_CENTER);
            $row->add_text_cell(text => $d->[3], halign => DC_HALIGN_LEFT);
        }
        $self->add_block_table(table => $table);
        $self->add_block_separator(size => DC_SIZE_XS);
    }

    return $self;
}

1;
