package DivCard::Testcard;

use rules;
use MP::Stopdebug;

use MP::Logit qw(dmp logit);
use MP::Utils;

use base qw(DivCard::Base::Card);

use DivCard::Base::Constants;
use DivCard::Base::Utils qw(colored);

use MordaX::Utils;

use constant {
    POSTFIX_TEXT  => 'STAFF ONLY',
    POSTFIX_COLOR => '#E2494E',
    FEEDBACK_TEXT => 'Пожаловаться',
};

use constant TITLE_POSTFIX => DC_HTML_NO_BREAK_SPACE x 4 . colored(POSTFIX_TEXT, POSTFIX_COLOR);

sub make {
    my ($self, $req, $card) = @_;
    $self->die_on_error(1);
    my $extra_menu = [
        { text => FEEDBACK_TEXT, url => "mailto:$card->{'feedback'}" },
    ];
    return $self->init_from_card($card,
        extra_menu_list   => $extra_menu,
        title_postfix     => TITLE_POSTFIX,
        check_title_count => 1,
    );
}

# %args = (
#     extra_menu_list   => [ {text => 'bla-bla', url => 'http://ya.ru'}, ],
#     title_postfix     => 'bla-bla',
#     check_title_count => [true|false],
# )
sub init_from_card {
    my ($self, $card, %args) = (shift, shift, @_);
    my $data        = $card->{'data'};
    my $data_states = $data->{'states'};

    return $self->error('failed to init_from_card: states are not array size')
      unless is_array_size $data_states;

    my $states      = $self->{'states'};
    my $states_hash = $self->{'states_hash'};
    my $menu_items  = $self->menu_items(@_);

    for my $state (@$data_states) {
        unless (is_hash_size $state) {
            $self->warning('init_from_card: state is not hash size');
            next;
        }
        my $id = int($state->{'state_id'});

        if ($states_hash->{$id}) {
            $self->warning("init_from_card: skip duplicated state with id = $id");
            next;
        }

        unless (is_array_size $state->{'blocks'}) {
            $self->warning("init_from_card: skip state without blocks");
            next;
        }

        my $title_count = 0;
        my $title_postfix = $args{'title_postfix'};
        for my $block (@{ $state->{'blocks'} }) {
            next unless is_hash_size $block and $block->{'type'} eq 'div-title-block';
            if ($menu_items) {
                $block->{'menu_items'} = $menu_items;
            }
            else {
                delete $block->{'menu_items'};
            }
            $block->{'text'} .= $title_postfix if $title_postfix;
            $title_count++;
        }
        if ($title_count != 1 and $args{'check_title_count'}) {
            $self->warning(
                "init_from_card: skip state that has $title_count count of title blocks"
            );
            next;
        }

        $states_hash->{$id} = $state;
        push @$states, $state;
        $state->{'state_id'} = int($id);
    }

    $self->{'background'} = $data->{'background'} if is_array_size $data->{'background'};

    return $self;
}

sub _prepare_states {
    my $self = shift;
    my @ready;
    for my $state (@{ $self->{'states'} }) {
        my $blocks =  $state->{'blocks'};
        next unless is_array_size $blocks;
        $state->{'blocks'} = $blocks;
        push @ready, $state;
    }
    $self->{'states'} = \@ready;
    return $self;
}


1;
