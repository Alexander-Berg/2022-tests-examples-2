package Perl::Critic::Policy::Home::AppVersionStrict;

use strict;
use warnings FATAL => 'all';
no if $] >= 5.017011, warnings => 'experimental::smartmatch';
use utf8;
use v5.14;

use Perl::Critic::Utils qw( :severities  );
use base qw(Perl::Critic::Policy);

use constant DESC => 'Manual usage of "app_version" is prohibited';
use constant EXPL => 'Use MordaX::Type::is_required_app_version instead';

sub supported_parameters { () }

sub default_severity {$SEVERITY_HIGH}

sub default_themes {qw(home bugs)}

# {XXXX} и $xxxxx
sub applies_to {qw(PPI::Token::Symbol PPI::Structure::Subscript)}

sub violates {
    my ($self, $elem) = @_;

    # быстрая проверка на вхождение app_version для возврата как можно раньше
    return if index(lc $elem->content, 'app_version') == -1;
    # медленная проверка
    return unless $elem->content =~ m/\bapp_version\b/i;

    # ищем statement куда входит наше выражение
    my $statement = $elem->parent;
    while (defined $statement and not $statement->isa('PPI::Statement')) {
        $statement = $statement->parent;
    }
    return unless defined $statement and $statement->isa('PPI::Statement');

    # если statement входит в conditional, то ругаемся сразу
    my $conditional = $statement->parent;
    while (defined $conditional
        and not $conditional->isa('PPI::Structure::Condition')
      ) {
        $conditional = $conditional->parent;
    }
    if (defined $conditional and $conditional->isa('PPI::Structure::Condition')) {
        return $self->violation(DESC, EXPL . ": $conditional", $elem);
    }

    # тут отсеим списочный контекст (обычно передача в функцию или хеш и т.д.)
    # проверять что родитель существует уже не нужно - было выше
    my $granny = $elem->parent->parent;
    return if defined $granny and $granny->isa('PPI::Structure::List');

    return $self->violation(DESC, EXPL . ": $statement", $elem);
}

1;
