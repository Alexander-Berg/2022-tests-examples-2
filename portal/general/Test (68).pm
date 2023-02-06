package MordaX::Experiment::AB::Tree::Node::Test;
use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use MP::Logit qw(dmp);

use MordaX::Experiment::AB::Tree::Constants;
use MTH;

use Test::More;
use Sub::Name;
use Scalar::Util qw(weaken);
use Scope::Guard;
use Symbol qw(qualify_to_ref);

use constant BASE_CLASS => 'MordaX::Experiment::AB::Tree::Node';

sub package {'MordaX::Experiment::AB::Tree::Node'}

sub class {'MordaX::Experiment::AB::Tree::Node'}

sub simple_node {
    shift; MordaX::Experiment::AB::Tree::Node::Test::Simple->new(@_)
}

sub true_node { MordaX::Experiment::AB::Tree::Node::Test::True->new() }

sub false_node { MordaX::Experiment::AB::Tree::Node::Test::False->new() }

sub undef_node { MordaX::Experiment::AB::Tree::Node::Test::Undef->new() }

sub expected_double_op {''}

sub isa_test {
    my ($self, $instance) = @_;
    isa_ok($instance, BASE_CLASS);
    isa_ok($instance, $self->class);
    return $self;
}

sub new_tests_setup : Test(startup) {
    my ($self) = @_;
    my $node1  = $self->simple_node(1);
    my $node2  = $self->simple_node(2);
    return $self->{new_tests} = [
        {
            name     => 'without args',
            args     => [],
            errors   => 1,
            expected => undef,
        },
        {
            name     => 'one arg',
            args     => ['some_arg'],
            errors   => 0,
            expected => ['some_arg', undef],
        },
        {
            name     => 'two args 1st not base class',
            args     => ['some_arg', $self->simple_node(1)],
            errors   => 1,
            expected => undef,
        },
        {
            name     => 'two args 2nd not base class',
            args     => [$self->simple_node(1), 'some_arg'],
            errors   => 1,
            expected => undef,
        },
        {
            name     => 'two correct args',
            args     => [$node1, $node2],
            errors   => 0,
            expected => [$node1, $node2],
        },
        {
            name     => 'three args',
            args     => [qw(too many args)],
            errors   => 1,
            expected => undef,
        },
    ];
}

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok($self->package);
    $self->isa_test($self->class);
    return;
}

sub redefine_logit_setup : Test(setup) {
    my ($self) = @_;
    state $_self     = undef;
    state $redefined = 0;
    weaken($_self = $self);
    return if $redefined;
    my $name = BASE_CLASS . '::logit';
    my $sym  = qualify_to_ref($name);
    no warnings qw(redefine);
    *$sym = subname $name => sub {
        ($_self && $_self->{logit_cb})
          ? $_self->{logit_cb}->(@_)
          : fail("called $name(" . explain_args(@_) . ")");
        1;
    };
    $redefined = 1;
}

sub redefine_error_setup : Test(setup) {
    weaken(my $self = shift);
    my $name = $self->class . '::error';
    my $sym  = qualify_to_ref($name);
    my $sub  = *$sym{CODE};
    no warnings qw(redefine);
    $self->{_error_scope} = Scope::Guard->new(sub {
            $sub ? *$sym = subname $name => $sub : undef(*$sym);
            1;
    });
    *$sym = subname $name => sub {
        ($self && $self->{error_cb})
          ? $self->{error_cb}->(@_)
          : fail(
            'called ' . $self->class . '->error('
              . explain_args(@_[1 .. $#_])
              . ')'
          );
        undef;
    };
    return $self;
}

sub redefine_error_cleanup : Test(teardown) {
    my ($self) = @_;
    delete $self->{_error_scope};
    return $self;
}

sub error_cb_cleanup : Test(teardown) {
    my ($self) = @_;
    delete $self->{error_cb};
    return $self;
}

sub error_cb {
    my ($self, $cb) = @_;
    $self->{error_cb} = $cb;
    return $self;
}

sub logit_cb_cleanup : Test(teardown) {
    my ($self) = @_;
    delete $self->{logit_cb};
    return $self;
}

sub logit_cb {
    my ($self, $cb) = @_;
    $self->{logit_cb} = $cb;
    return $self;
}

sub test_error : Tests {
    my ($self) = @_;
    # restore real method
    $self->redefine_error_cleanup;
    my @got;
    $self->logit_cb(sub { @got = @_; undef; });
    my @expected = ('interr', 'some error text');
    my $ret = $self->class->error(q(some error text));
    is_deeply(\@got, \@expected, "error method calls logit with correct args");
    is($ret, undef, 'error method returns undef');
    my @list = $self->class->error(q(some error text));
    ok(
        ($#list == 0 and not defined $list[0]),
        'list context: error method returns undef',
    );
    return $self;
}

sub test_new : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->error_cb(sub { $errors++ });
    for my $test (@{ $self->{new_tests} }) {
        $errors = 0;
        my $name = 'test new ' . $test->{name};
        my $obj  = $self->class->new(@{ $test->{args} });
        is($errors, $test->{errors} // 0, "$name errors count");
        if (my $expected = $test->{expected}) {
            ok($obj, "$name object created")
              or next;
            $self->isa_test($obj);
            is(
                $obj->[ABT_LEFT],
                $expected->[ABT_LEFT],
                "$name left subtree ok",
            );
            is(
                $obj->[ABT_RIGHT],
                $expected->[ABT_RIGHT],
                "$name right subtree ok",
            );
        }
        else {
            is($obj, undef, "$name returns undef");
            $name   = 'list context: ' . $name;
            $errors = 0;
            my @list = $self->class->new(@{ $test->{args} });
            is($errors, $test->{errors} // 0, "$name errors count");
            ok(
                ($#list == 0 and not defined $list[0]),
                "$name returns undef",
            );
        }
    }
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->error_cb(sub { $errors++ });
    my $obj = $self->class->new(1);
    my $ret = $obj->evaluate();
    ok(not($ret), 'evaluate returns false');
    is($errors, 1, 'evaluate method must be redefined');
    return $self;
}

sub test_double_op : Tests {
    my ($self) = @_;
    is($self->class->_double_op, $self->expected_double_op);
    return $self;
}

sub test_subnode_as_string : Tests {
    my ($self) = @_;
    if ($self->class ne BASE_CLASS) {
        ok('test subnode_as_string need only for ' . BASE_CLASS);
        return $self;
    }
    my $obj_string = $self->class->new('string');
    is($obj_string->subnode_as_string(ABT_LEFT), 'string');
    my $obj_with_node = $self->class->new($obj_string);
    is($obj_with_node->subnode_as_string(ABT_LEFT), 'string');
    return $self;
}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    my $obj = $self->class->new($self->class->new('string'));
    is($obj->as_string, 'string');
    return $self;
}

sub test_as_string_two_nodes : Tests {
    my ($self) = @_;
    my $left   = $self->simple_node('left');
    my $right  = $self->simple_node('right');
    my $obj = $self->class->new($left, $right);
    is($obj->as_string, '(left) ' . $self->expected_double_op . ' (right)');
    return $self;
}

package MordaX::Experiment::AB::Tree::Node::Test::Simple;

use mro;

use base qw(MordaX::Experiment::AB::Tree::Node);

sub evaluate { $_[0]->[0] }

package MordaX::Experiment::AB::Tree::Node::Test::True;

use mro;

use base qw(MordaX::Experiment::AB::Tree::Node);

sub new { shift->next::method(1) }

sub evaluate {1}

package MordaX::Experiment::AB::Tree::Node::Test::False;

use mro;

use base qw(MordaX::Experiment::AB::Tree::Node);

sub new { shift->next::method(0) }

sub evaluate {0}

package MordaX::Experiment::AB::Tree::Node::Test::Undef;

use mro;

use base qw(MordaX::Experiment::AB::Tree::Node);

sub new { shift->next::method(undef) }

sub evaluate {undef}


1;
