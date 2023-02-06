package Perl::Critic::Policy::Home::ValidateArgs::Is_required_app_version;

use strict;
use warnings FATAL => 'all';
no if $] >= 5.017011, warnings => 'experimental::smartmatch';
use utf8;
use v5.14;

use Perl::Critic::Utils qw( :severities :classification :ppi );
use Scalar::Util qw(blessed looks_like_number);

use base qw(Perl::Critic::Policy);

use constant DESC => 'Validation of call MordaX::Type::is_required_app_version';

use constant SUB_NAMES => qw(
  MordaX::Type::is_required_app_version
  is_required_app_version
);

use constant APP_VERSIONS => qw(
    android
    iphone
    win_phone
);

sub supported_parameters { () }

sub default_severity {$SEVERITY_HIGH}

sub default_themes {qw(home bugs)}

sub applies_to {qw(PPI::Token::Word)}

sub violates {
    my ($self, $elem) = @_;
    # проверяем что PPI::Token::Word принадлежит массиву SUB_NAMES
    return unless $elem->content ~~ [(SUB_NAMES)];
    # проверяем что это вызов функции
    return unless is_function_call($elem);

    # получаем аргументы функции
    my @args = parse_arg_list($elem);

    # проверяем кол-во аргументов
    unless (@args == 2) {
        return $self->violation(DESC, '2 args expected', $elem);
    }

    # запрещаем сложный вызов функции (только $req и {})
    unless (@{ $args[0] } == 1 and @{ $args[1] } == 1) {
        return $self->violation(DESC, 'only simple call of function is allowed', $elem);
    }

    # проверяем что первый аргумент $req
    unless (
        @{ $args[0] } == 1
        and blessed($args[0]->[0])
        and $args[0]->[0]->isa('PPI::Token::Symbol')
        and $args[0]->[0]->content eq '$req'
      ) {
        return $self->violation(DESC, 'first argument must be $req', $elem);
    }

    # Проверяем, что второй аргумент это ссылка на хеш, заданная в самой
    # функции, а не передающаяся как переменная
    unless (
        @{ $args[1] } == 1
        and blessed($args[1]->[0])
        and $args[1]->[0]->isa('PPI::Structure::Constructor')
        and $args[1]->[0]->braces eq '{}'
    ) {
        return $self->violation(DESC, 'second argument must be hash constructor', $elem);
    }

    # Проверяем внутренности хеша на опечатки
    my $hash = $args[1]->[0];
    my $hash_statement = ($hash->children)[0];

    # первый элемент должен быть PPI::Statement иначе это странная конструкция
    # и мы молча выходим
    return unless blessed($hash_statement)
      and $hash_statement->isa('PPI::Statement');

    # цикл по элементам внутри конструкции
    for my $child ($hash_statement->children) {
        my $content;
        # Если это ключ хеша без кавычек
        if ($child->isa('PPI::Token::Word') and is_hash_key($child)) {
            $content = $child->content;
        }
        # Если это строка с кавычками
        elsif ($child->isa('PPI::Token::Quote')) {
            $content = eval $child->content;
            # пропускаем если будет версия ПП забитая в виде строки
            next if looks_like_number($content);
        }

        # не смогли получить content - молча скипаем
        next unless defined $content;

        unless ($content ~~ [(APP_VERSIONS)]) {
            return $self->violation(DESC, "unknown app_platform = '$content'", $elem);
        }
    }

    return;
}

1;
