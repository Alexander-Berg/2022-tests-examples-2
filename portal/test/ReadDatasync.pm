package Test::ReadDatasync;
use TestHelper qw(no_register);
# Смотрелка бд датасинка
use rules;
use MP::Stopdebug;

use MordaX::Config;
use MordaX::Output;
use MordaX::Utils;
use MP::DTS;
use MP::Logit;
use MP::Utils;
use Rapid::Base;
use Rapid::Req;

my $main_bases = {
    1 => '/v1/personality/profile/search_app/configs_topics',
    2 => '/v1/personality/profile/search_app_beta/configs_topics',
    3 => '/v1/personality/profile/morda/desktopnotifications',
    4 => '/v1/personality/profile/morda/usersettings',
    5 => '/v1/personality/profile/loyality_cards',
};

my $bases = {
    %$main_bases,
    6 => '/v1/personality/profile/addresses/morda',
    7 => '/v1/personality/profile/extracted_addresses',
};

sub handler {

    return unless $MordaX::Config::TestingInstance;

    my ($req) = @_;

    my $res = &datasync;

    return MordaX::Output::r200json($req, $res, [], undef, {}) if defined $res;
    # возвращаем не 200, чтобы клиент сам ретраил запросы
    return MordaX::Output::respond($req, undef, [], 'text/plain', undef, status => '204 No Content');
}

sub datasync {
    my ($req) = @_;

    MordaX::Auth::auth($req, response => {}, no_redirect => 1);

    my $base = int(MP::Utils::number($req->{Getargshash}{base}));
    my $uid  = int(MP::Utils::number($req->{Getargshash}{uid}));
    if ($req->{UID} && $base && $bases->{ $base }) {
        if ($uid && $uid > 0) {
            $req->{custom_datasync_user_uid} = $uid;
        }
        else {
            $uid = -1;
        }
        my $request_id;
        if ($base ~~ [qw(1 2)]) {
            $request_id = MP::DTS::init_configs_topics($req, $uid, $base == 2);
        }
        elsif ($base == 3) {
            $request_id = MP::DTS::init_dntf($req, $uid);
        }
        elsif ($base == 4) {
            $request_id = MP::DTS::init_user_settings($req, $uid);
        }
        elsif ($base == 5) {
            $request_id = MP::DTS::init_bonus_cards($req, $uid);
        }
        elsif ($base == 6) {
            $request_id = MP::DTS::init_addresses($req, $uid);
        }
        elsif ($base == 7) {
            $request_id = MP::DTS::init_extracted_points($req, $uid);
        }

        return { error => 'No request_id' } unless $request_id;

        my $http = MordaX::HTTP->new($req);
        my $http_alias = MP::DTS::run_request($req, $uid);
        my $req_info = $http->{handler}->{aliases}->{$http_alias};
        my $response = MP::DTS::personal_storage_response($req, $request_id);

        return { error => 'No answer' } unless is_hash_size $response;

        $response->{http_req_headers}    = $req_info->{headers};
        $response->{http_req_origurl}    = $req_info->{origurl};
        $response->{http_req_post_data}  = $req_info->{post_data};
        $response->{http_req_error}      = $req_info->{error};
        $response->{http_req_error_text} = $req_info->{error_text};

        return $response;
    }
    else {
        return &help;
    }
}

sub help {
    my ($req) = @_;
    return {
        bases    => $main_bases,
        datasync => 'https://${testing}.yandex.ru/test/datasync?[uid=${puid}&]base=${base_id}',
        $req->{UID} ? (help => 'Вы уже авторизованы, спасибо') : (help => 'Для работы скрипта вы должны быть авторизованы'),
    };
}


1;
