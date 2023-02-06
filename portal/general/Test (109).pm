package MordaX::Stream::Personalization::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Stream::Personalization;

sub _startup : Test(startup) {
}

sub _setup : Test(setup) {
    my $self = shift;
}

sub test_modify_data_for_notification : Test(3) {
    my $self = shift;

    *modify_data_for_notification = \&MordaX::Stream::Personalization::modify_data_for_notification;

    my $in = {
        catchup_age        =>  259200,
        channel_content_id =>  "44714eae223f8af398ea86f676b73ed7",
        channel_id         =>  100004,
        channel_name       =>  "Советское кино",
        content_id         =>  "48fa50ea2a1bb43f98a290267f86a419",
        program_title      =>  "Зимний вечер в Гаграх"
    };

    my $out_exp = {
        channel_id         =>  $in->{channel_id},
        channel_name       =>  $in->{channel_name},
        content_id         =>  $in->{content_id},
        program_title      =>  $in->{program_title}
    };

    is_deeply(modify_data_for_notification($in), $out_exp);

    $in = {
        channel_content_id =>  "44714eae223f8af398ea86f676b73ed7",
        channel_id         =>  100004,
        channel_name       =>  "Советское кино",
        content_id         =>  "48fa50ea2a1bb43f98a290267f86a419",
        program_title      =>  "Зимний вечер в Гаграх"
    };

    $out_exp = {
        channel_id         =>  $in->{channel_id},
        channel_name       =>  $in->{channel_name},
        content_id         =>  $in->{channel_content_id},
        program_title      =>  $in->{program_title}
    };

    is_deeply(modify_data_for_notification($in), $out_exp);

    $in = {
        catchup_age        =>  0,
        channel_content_id =>  "44714eae223f8af398ea86f676b73ed7",
        channel_id         =>  100004,
        channel_name       =>  "Советское кино",
        content_id         =>  "48fa50ea2a1bb43f98a290267f86a419",
        program_title      =>  "Зимний вечер в Гаграх"
    };

    $out_exp = {
        channel_id         =>  $in->{channel_id},
        channel_name       =>  $in->{channel_name},
        content_id         =>  $in->{channel_content_id},
        program_title      =>  $in->{program_title}
    };

    is_deeply(modify_data_for_notification($in), $out_exp);
}



1;
