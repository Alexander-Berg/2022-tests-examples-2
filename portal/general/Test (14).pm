package DivCardV2::Base::Object::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use MTH;

use Test::More;
use Scalar::Util qw(weaken);

use DivCardV2::Base::Constants;

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok('DivCardV2::Base::Object');
    return;
}

# NOTE: так как модуль вызывает MP::Logit::set_logit_subtype, то:
#        * при переопределении logit, subtype потеряется из стека
#        * переопределять logit надо не в startup!
sub redefine_logit : Test(setup) {
    my ($self) = @_;
    state $_self     = undef;
    state $redefined = 0;
    weaken($_self = $self);
    return if $redefined;
    no warnings qw(redefine);
    no strict qw(refs);
    *DivCardV2::Base::Object::logit = sub {
        ($_self && $_self->{logit_cb}) ? $_self->{logit_cb}->(@_) : undef;
    };
    $redefined = 1;
    return;
}

# Так же эти два метода выполняют косвенную проверку scope, vscope и escope.
# Если они не будут работать, то разлетятся остальные тесты.
sub scope_create : Test(setup) {
    my ($self) = @_;
    $self->{guard} = DCV2_BCLS->scope();
    return;
}

sub scope_cleanup : Test(teardown) {
    my ($self) = @_;
    delete $self->{guard};
    return;
}

sub version : Tests {
    my ($self) = @_;
    is(DCV2_BCLS->version, DCV2_MIN_VERSION, "Default version " . DCV2_MIN_VERSION);
    DCV2_BCLS->version('3.0.0');
    is(DCV2_BCLS->version, '3.0.0', "Version change ok");
    return;
}

sub is_required_version : Tests {
    my ($self) = @_;
    ok(DCV2_BCLS->is_required_version('1.0.0'));
    ok(DCV2_BCLS->is_required_version('2.0.0'));
    ok(not DCV2_BCLS->is_required_version('2.0.1'));
    DCV2_BCLS->version('2.010.0');
    ok(DCV2_BCLS->is_required_version('1.0.0'));
    ok(DCV2_BCLS->is_required_version('2.0.0'));
    ok(DCV2_BCLS->is_required_version('2.0.1'));
    ok(not DCV2_BCLS->is_required_version('2.10.1'));
    ok(not DCV2_BCLS->is_required_version('2.11.0'));
    return;
}

sub version_from_api_search : Tests {
    my ($self) = @_;
    my @tests = (
        [[android => 6000000] => undef],
        [[android => 8000000] => '2.0.0'],
        [[android => 9000000] => '2.0.0'],
        [[iphone  => 4000000] => undef],
        [[iphone  => 5000000] => '2.0.0'],
        [[iphone  => 6000000] => '2.0.0'],
    );
    for (@tests) {
        my ($args, $expected) = @$_;
        my $fake_version = '1.0.0';
        DCV2_BCLS->version($fake_version);
        $expected //= $fake_version;
        DCV2_BCLS->version_from_api_search(@$args);
        is(DCV2_BCLS->version, $expected);
    }
    return;
}

sub error_handle_default_args : Tests {
    my ($self) = @_;
    my @args = qw(some error array);
    my @ret;
    local $self->{logit_cb} = sub { @ret = @_ };
    DCV2_BCLS->error(@args);
    is(shift(@ret), 'interr', 'call logit with interr');
    is_deeply(\@ret, \@args, 'other args');
    @ret = ();
    DCV2_BCLS->warning(@args);
    is(shift(@ret), 'warning', 'call logit with warning');
    is_deeply(\@ret, \@args, 'other args');
    return;
}

sub eprefix : Tests {
    my ($self) = @_;
    is(DCV2_BCLS->eprefix, undef, 'by default no prefix');
    my $prefix = 'prefix';
    is(DCV2_BCLS->eprefix($prefix), DCV2_BCLS, 'returns self');
    is(DCV2_BCLS->eprefix,          $prefix,   'prefix was set');
    my @ret;
    local $self->{logit_cb} = sub { @ret = @_ };
    DCV2_BCLS->error('test');
    is($ret[1], $prefix, 'prefix in error method');
    @ret = ();
    DCV2_BCLS->warning('test');
    is($ret[1], $prefix, 'prefix in warning method');
    return;
}

sub on_warning_default : Tests {
    my ($self) = @_;
    DCV2_BCLS->on_warning_die;
    DCV2_BCLS->on_warning_default;
    my $called = 0;
    local $self->{logit_cb} = sub { $called++ };
    DCV2_BCLS->warning('test');
    ok($called);
    return;
}

sub on_warning_die : Tests {
    my ($self) = @_;
    my $prefix = 'prefix';
    DCV2_BCLS->on_warning_die;
    DCV2_BCLS->eprefix($prefix);
    my $died = 1;
    eval { DCV2_BCLS->warning(qw(some error array)); $died = 0; };
    like($@, qr/^$prefix some error array/);
    ok($died);
    return;
}

sub on_warning_quiet : Tests {
    my ($self) = @_;
    my $prefix = 'prefix';
    DCV2_BCLS->on_warning_quiet;
    DCV2_BCLS->eprefix($prefix);
    my $called = 0;
    local $self->{logit_cb} = sub { $called++ };
    DCV2_BCLS->warning('test');
    ok(not $called);
    return;
}

sub on_warning_cb : Tests {
    my ($self) = @_;
    my @ret;
    DCV2_BCLS->on_warning_cb(sub { @ret = @_; });
    DCV2_BCLS->eprefix('prefix');
    DCV2_BCLS->warning(qw(some error array));
    is_deeply(\@ret, [qw(prefix some error array)]);
    return;
}

sub on_error_default : Tests {
    my ($self) = @_;
    DCV2_BCLS->on_error_die;
    DCV2_BCLS->on_error_default;
    my $called = 0;
    local $self->{logit_cb} = sub { $called++ };
    DCV2_BCLS->error('test');
    ok($called);
    return;
}

sub on_error_die : Tests {
    my ($self) = @_;
    my $prefix = 'prefix';
    DCV2_BCLS->on_error_die;
    DCV2_BCLS->eprefix($prefix);
    my $died = 1;
    eval { DCV2_BCLS->error(qw(some error array)); $died = 0; };
    like($@, qr/^$prefix some error array/);
    ok($died);
    return;
}

sub on_error_quiet : Tests {
    my ($self) = @_;
    my $prefix = 'prefix';
    DCV2_BCLS->on_error_quiet;
    DCV2_BCLS->eprefix($prefix);
    my $called = 0;
    local $self->{logit_cb} = sub { $called++ };
    DCV2_BCLS->error('test');
    ok(not $called);
    return;
}

sub on_error_cb : Tests {
    my ($self) = @_;
    my @ret;
    DCV2_BCLS->on_error_cb(sub { @ret = @_; });
    DCV2_BCLS->eprefix('prefix');
    DCV2_BCLS->error(qw(some error array));
    is_deeply(\@ret, [qw(prefix some error array)]);
    return;
}

1;
