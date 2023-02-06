package MTH;

# Morda Test Helpers

use strict;
use warnings FATAL => 'all';
no  warnings 'experimental::smartmatch';
use v5.14;
use utf8;
use mro;

use base qw(Exporter Test::Builder::Module);

our @EXPORT = qw(is_json_number is_json_string explain_args explain_args_hash mock_options);

use JSON::XS;
use Data::Dumper;
use Scalar::Util qw(looks_like_number);

sub mock_options {
    my ($true_arr, $vals_hash) = @_;
    $true_arr  ||= [];
    $vals_hash ||= {};
    no warnings 'redefine';
    *MordaX::Utils::options = sub {
        if (exists $vals_hash->{$_[0]}) {
            return $vals_hash->{$_[0]};
        }
        if ($_[0] ~~ [@$true_arr]) {
            return 1;
        }
        return undef;
    };
    *MordaX::Utils::is_option_turned_by_host = sub ($$) {
        if ($_[1] ~~ [@$true_arr]) {
            return 1;
        }
        return 0;
    };
    use warnings 'redefine';
}

sub is_json_number ($;$) {
    my $tb = __PACKAGE__->builder();
    my $json = eval { JSON::XS->new()->utf8(1)->encode([$_[0]]) };
    unless ($json) {
        $tb->ok(0, $_[1]);
        $tb->diag($@);
        return;
    }
    $json =~ s/^\[|\]$//g;
    return $tb->ok(looks_like_number($json), $_[1]);
}

sub is_json_string ($;$) {
    my $tb = __PACKAGE__->builder();
    my $json = eval { JSON::XS->new()->utf8(1)->encode([$_[0]]) };
    unless ($json) {
        $tb->ok(0, $_[1]);
        $tb->diag($@);
        return;
    }
    $json =~ s/^\[|\]$//g;
    return $tb->ok($json =~ m/^".*"$/, $_[1]);
}

sub explain_args (@) {
    my $args = [@_];
    my $ret = eval {
        Data::Dumper->new([$args])
          ->Indent(0)
          ->Pair(' => ')
          ->Terse(1)
          ->Sortkeys(1)
          ->Useperl(0)
          ->Useqq(1)
          ->Deepcopy(1)
          ->Dump()
    } or return 'undef';
    $ret =~ s/^\[|\]$//g;
    return $ret;
}

sub explain_args_hash (@) {
    my $args = {@_};
    my $ret = eval {
        Data::Dumper->new([$args])
          ->Indent(0)
          ->Pair(' => ')
          ->Terse(1)
          ->Sortkeys(1)
          ->Useperl(0)
          ->Useqq(1)
          ->Deepcopy(1)
          ->Dump()
    } or return 'undef';
    $ret =~ s/^\{|\}$//g;
    return $ret;
}

1;

