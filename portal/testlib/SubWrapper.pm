package SubWrapper;

use strict;
use warnings FATAL => 'all';
use utf8;
use v5.14;

use Data::Dumper;

sub modify_namespace {
    no strict 'refs';
    no warnings 'redefine';

    state $visited = {};

    # LOOP over namespaces
    my @stack = ('main::');
    while (defined(my $sym = shift @stack)) {
        # last index of "::"
        my $i = rindex($sym, '::');
        # "::" at the end of string - we have another namespace
        if ($i + 2 == length($sym)) {
            push @stack, map { $sym . $_ } grep { $_ ne 'main::' } keys %{"$sym"};
            next;
        }

        # we are interested at only code refs
        next unless *{"$sym"}{'CODE'};
        # if we already saw this sub
        next if $visited->{$sym}++;

        # split by the last "::" :
        # $sym       = A::B::C::D
        # $namespace = A::B::C::
        # $name      = D
        my $namespace = substr($sym, 0, $i + 2);
        my $name = substr($sym, $i + 2);

        if ($name eq 'logit' or $name eq 'dmp') {
            next if ${"$namespace"}{'LOGIT_OK'};
            (my $subname = $sym) =~ s/^main:://;
            *{"$sym"} = sub {
                unshift @_, $subname;
                goto &logit_wrapper;
            };
        }

        # After calling use_ok we need to loop over namespaces second time
        if ($name eq 'use_ok') {
            my $real_sub = \&{"$sym"};
            *{"$sym"} = sub ($;@) {
                eval qq(use $_[0]);
                &modify_namespace;
                goto \&$real_sub;
            }
        }

        # do not write anything
        if ($namespace =~ m/Pfile::$/) {
            no warnings qw(prototype);
            *{"$sym"} = sub {1};
        }
    }
}

INIT {
    no strict 'refs';
    no warnings 'redefine';

    # return if it is not test
    return unless *{'Test::More::fail'}{'CODE'};
    &modify_namespace;
}


sub logit_wrapper {
    my $subname = shift;
    my @backtrace;
    for (0 .. 6) {
        my @caller_info = caller($_);
        last unless (@caller_info);
        my $chunk = join(':', $caller_info[0], $caller_info[2]);
        unshift @backtrace, $chunk;
        last if ($caller_info[0] eq 'main');
    }
    my $args = Data::Dumper->new([\@_])
      ->Indent(0)
      ->Terse(1)
      ->Maxdepth(1)
      ->Dump();
    &Test::More::fail(
        "Called $subname with args: $args trace: "
          . join('-->', @backtrace)
    );
}

1;

