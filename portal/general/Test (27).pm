package HelloWorld::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use Handler::HelloWorld;

use MP::Logit qw(dmp logit);

sub test_cut_out_token : Test(13) {
    my $self = shift;

    no warnings qw(redefine experimental::smartmatch);
    *cut_out_token = \&Handler::HelloWorld::cut_out_token;

    #
    # === undefined, empty string, zero, string, number
    #

    is(cut_out_token(undef), undef, 'undef');
    is(cut_out_token(''), '', 'empty string');
    is(cut_out_token(0), 0, 'zero');
    is(cut_out_token('abc'), 'abc', 'string');
    is(cut_out_token(123), 123, 'number');

    #
    # === ref of: undefined, empty string, zero, string, number
    #

    is(${ cut_out_token(\undef) }, undef, 'ref of undef');
    is(${ cut_out_token(\'') }, '', 'ref of empty string');
    is(${ cut_out_token(\0) }, 0, 'ref of zero');
    is(${ cut_out_token(\'abc') }, 'abc', 'ref of string');
    is(${ cut_out_token(\123) }, 123, 'ref of number');

    #
    # === ref of array of numbers
    #
   
    my $tests_data = '[1,2]';
    is(${ cut_out_token(\$tests_data) }, $tests_data, 'ref of array of numbers');

    #
    # === ref of valid data
    #

    $tests_data = '{"a":"1"}';
    is(${ cut_out_token(\$tests_data) }, $tests_data, 'ref of valid json without array');

    $tests_data = '[{"uid":"123","token":"XXX"},{"uid":"456","token":"XXX"}]';
    my $result = '[{"uid":"123"},{"uid":"456"}]';
    is(${ cut_out_token(\$tests_data) }, $result, 'ref of valid json with array');
}

1;
