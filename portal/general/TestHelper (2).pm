# TestHelper from MordaX project
# -*- mode: cperl; encoding: utf-8 -*-
# coding: utf8
#
# Yandex, 2009

package TestHelper;
use rules;
use MP::Stopdebug;

# Tooo old code
## no critic (BuiltinFunctions::ProhibitUniversalCan)
## no critic (BuiltinFunctions::ProhibitUniversalIsa)

use JSON::XS;
use MP::UserAgent;
use MIME::Base64;
use Data::Dumper;
use Time::HiRes;
use URI::Escape::XS;
use Handler::Utils_serialize;
use MordaX::Auth;
use MordaX::Logit;
use MordaX::Utils;
use MordaX::Conf;
use MordaX::Config;
use MordaX::Cache;
use MordaX::Nets;
use MordaX::Input;
use MordaX::Widgets::Utils;
use MordaX::Data;
use MordaX::Data_get;
use Geo;
use Geo::Domain;
use Geo::Lang;
use MordaX::Banners;
use MordaX::Experiment;
use MordaX::Experiment::AB::Helper;
use MordaX::Experiment::AB::Flags;
use MP::Utils;
use MP::Time;
use MordaX::Data_load;
use MordaX::Tmpl;
use WBOX::Wauth;
use WBOX::Storage::WSettings;
use MordaX::DetectDevice;
use DNS;
use Yandexuid;
use Test::Dumps;
use Test::Personal;
use Test::UserInfo;
use Test::GeobaseCompare;
use Test::Devs;
use Test::Handlers;
use Test::Xiva;
use Test::PerlTest;
use Test::ReadDatasync;
use Test::ClearAll;
use Test::BlockDisplay;
use Test::ErrorLog;
use Test::ScriptLog;
use Test::ABCheck;
use Test::ABFlags;
use Test::FlagsAllowed;
use testlib::GeoHelper;

our %Pass = (
    '/test/blockdisplay/' => '*Test::BlockDisplay::handle',
    '/test/errorlog/'     => '*Test::ErrorLog::handle',
    '/test/scriptlog/'     => '*Test::ScriptLog::handle',
    '/test/handlers/'     => '*Test::Handlers::handle',
);
our %PostActions = (
    '/test/instant-post/' => \&post_Rapid_config,
    '/test/csp/'          => \&post_log_csp,
    '/test/kotepost/'     => \&handle_kote_post,
);
our %AvaliableActions = (
    '/test/'               => {'handler' => \&HelloWorld,},
    '/test/dummy/'         => {'handler' => \&Dummy,},
    '/test/setwcookie/'    => {'handler' => \&SetWCookie,},
    '/test/showwcookie/'   => {'handler' => \&ShowWCookie,},
    '/test/subscription/'  => {'handler' => \&Subscription,},
    '/test/subscribe/'     => {'handler' => \&Subscribe,},
    '/test/yandexuid/age/' => {'handler' => \&yandexuid_cookie_age,},
    '/test/yandexuid/'     => {'handler' => \&yandexuid_cookie_set,},
    '/test/sessionid/'     => {'handler' => \&set_sessionid,},
    '/test/yandex_gid/'    => {'handler' => \&set_yandex_gid_cookie,},
    '/test/interests/'     => {'handler' => \&handle_interests,},
    '/test/sites/'         => {'handler' => \&handle_sites,},
    '/test/hdr/'           => {'handler' => \&handle_headers,},
    '/test/ip/'            => {'handler' => \&handle_ip,},
    '/test/lang/'          => {'handler' => \&handle_lang,},
    '/test/geo/'           => {'handler' => \&handle_geo,},
    '/test/geoipsearch/'   => {'handler' => \&handle_geo_ip_search,},
    # DEPRECATED:
    '/test/mega/' => {'handler' => \&handle_megafon,},
    # END DEPRECATED
    '/test/my_parse/' => {'handler' => \&handle_my_parse,},
    '/test/id_slot/'  => {'handler' => \&handle_id_slot,},
    '/test/phone/'    => {'handler' => \&handle_phone,},
    '/test/harlog/'   => {'handler' => \&handle_harlog,},
    '/test/log/'      => {'handler' => \&handle_log,},
    '/test/form/'             => {'handler' => \&handle_form,},
    '/test/post/'             => {'handler' => \&handle_post,},
    '/test/302/'              => {'handler' => \&handle_302,},
    "/test/package/"          => {'handler' => \&handle_package,},
    '/test/version/install/'  => {'handler' => \&handle_install_version,},
    '/test/version/status/'   => {'handler' => \&handle_install_status,},
    '/test/version/'          => {'handler' => \&handle_version,},
    '/test/zerro/'            => {'handler' => \&handle_zerro_respond,},
    '/test/pixel/'            => {'handler' => \&handle_pixel_respond,},
    '/test/weather/'          => {'handler' => \&handle_weather_report,},
    '/test/instant/'          => {handler   => \&handle_Rapid_config},
    "/test/dumpvars/"         => {handler   => \&handle_dumpvars,},
    '/test/yabs/'             => {handler   => \&handle_yabs_stripe},
    '/test/ybcookie/'         => {handler   => \&handle_yb_cookie},
    '/test/banner/'           => {handler   => \&handle_yabs_stripe},
    '/test/display/'          => {handler   => \&handle_display},

    '/test/tv/'           => {handler   => \&handle_tv},
    '/test/dumps/'            => {handler   => '*Test::Dumps::handler',},
    '/test/personal/tickets/' => {handler   => '*Test::Personal::tickets',},
    '/test/personal/traffic/' => {handler   => '*Test::Personal::traffic',},

    '/test/clearall/' => {handler => '*Test::ClearAll::handler',},
    '/test/userinfo/' => {handler => '*Test::UserInfo::handler',},
    '/test/geo/cmp/'  => {handler => '*Test::GeobaseCompare::handler',},
    '/test/devs/'     => {handler => '*Test::Devs::handler',},
    '/test/xiva/'     => {handler => '*Test::Xiva::handler',},
    '/test/t/'        => {handler => '*Test::PerlTest::handler'},
    '/test/t/run/'    => {handler => '*Test::PerlTest::add'},
    '/test/t/add/'    => {handler => '*Test::PerlTest::add'},
    '/test/t/history/'=> {handler => '*Test::PerlTest::history'},
    '/test/t/report/' => {handler => '*Test::PerlTest::report'},
    '/test/t/status/' => {handler => '*Test::PerlTest::status'},
    '/test/datasync/' => {handler => '*Test::ReadDatasync::handler'},
    '/test/abcheck/'  => {handler => '*Test::ABCheck::handler'},
    '/test/abcheck/parse/'  => {handler => '*Test::ABCheck::parse_handler'},
    '/test/abflags/'  => {handler => '*Test::ABFlags::handler'},

    '/test/flags_allowed/'            => {handler   => '*Test::FlagsAllowed::handler',},

    '/test/inspect/'  => {'handler' => \&handle_node_dev_tools,},
    '/test/antiaddblock/'  => {'handler' => \&handle_antiaddblock},
    '/test/themes/'  => {'handler' => \&handle_themes},
    '/test/kote/'  => {'handler' => \&handle_kote},

    '/test/dzensearch/desktop/'  => {'handler' => \&handle_dzensearch_desktop},
    '/test/dzensearch/touch/'  => {'handler' => \&handle_dzensearch_touch},
);

sub handler {
    my ($r, $req) = @_;
    my $path = $r->path();
    if ($Pass{$path}) {
        return $Pass{$path}->($r, $req);
    }

    # HOME-77010: используется в автотестах инициализаии зависимостей АБ флагов
    if (MordaX::Options::options('anticipatory_init_ab_flags_for_autotests')) {
        $req->{handler_logs} = [];

        my $orig_ref = $MP::Logit::write_wrapper_ref;
        $MP::Logit::write_wrapper_ref = sub { push @{ $req->{handler_logs} }, { message => @_}; };

        logit('warning', 'Anticipatory AB Flags call');
        MordaX::Experiment::AB::flags($req)->flags();
        logit('warning', 'Restore original log wrapper');

        $MP::Logit::write_wrapper_ref = $orig_ref;
    }

    my $input = MordaX::Input->new(r => $r, req=>$req);

    unless ($input) {
        logit('interr', 'Cannot initialize user input');
        return 500;
    }

    # Hashed user's pattern
    unless ($req) {
        logit('interr', 'Cannot get user request from input module');
        return 500;
    }

    unless ($req->{'YandexInternal'}) {
        logit('interr', 'Not Yandex internal request');
        return MordaX::Output::notfound($req);
    }

    MordaX::Input::input_yandexuid($r, $req);

    my $postargs = $r->all_postargs();

    $req->{'_STATBOX_ID_SUFFIX_'} = 'test'; # HOME-37938
    my $auth = MordaX::Auth->new($req);
    $req->{'AuthOBJ'} = $auth;
    if ($auth->{'UID'}) {
        $req->{'UID'} = $auth->{'UID'};
    }

    # Предварительная подготовка хеша запроса
    my $data = {
        'Page'    => {},
        'cookies' => [],
    };

    #$data->{'Page'}->{'Hostname'} = $Input->{'Hostname'};
    #$data->{'Page'}->{'Retpath'} = uri_escape('http://' . $Input->{'Hostname'} . '/' . $Input->{'Uri'});

    $data->{'Page'}->{'NcRnd'} = int(1000000000 + rand(8999999999));

    my $uriarg  = undef;
    my $vaction = undef;
    my $action  = '/' . join('/', @{$req->{'UriChain'}}) . '/';

    # Если УРЛ состоит более, чем из двух секций, сохранить, "на всякий случай", последний токен и приготовить
    # переменную "virtual action", содержающую то же самое, но со служебным "{URIARG}"
    my @urichain = split(/\//, $action);
    if ((scalar(@urichain) > 2) && ($urichain[-1] =~ m,^[a-zA-Z0-9\-]+$,o)) {
        $uriarg       = $urichain[-1];
        $urichain[-1] = '{URIARG}';
        $vaction      = join('/', @urichain);
    }

    # Если действие для action не определено, а для virtual action -- определено, значит, это, действительно,
    # virtual action. В таком случае, надо передать последний токен в качестве UriArg (который, собственно, потом разбирать)
    if ($vaction && !defined($AvaliableActions{$action}) && defined($AvaliableActions{$vaction})) {
        $action = $vaction;
        $data->{'UriArg'} = $uriarg;
    }

    my $page = $data->{'Page'}->{'MordaPage'} = {};

    MordaX::Utils::sk_gen_lazy($req);
    $page->{yu} = $req->{'yu'};
    Handler::Utils_serialize::SerializePageVariables($req, $data->{'Page'}->{'MordaPage'});

    $page->{'InstanceSubname'} = $MordaX::Config::InstanceModifier . $MordaX::Config::Subdomain;

    # Все uri, кроме явно заданных как action, возвращают апачевский 404, для дальнейшей обработки
    if ($PostActions{$action}) {
        return $PostActions{$action}->($r, $req, $data);
    } elsif ($AvaliableActions{$action}) {
        # Проверяем наличие авторизации и, если режим не допускает анонимной работы, редиректим на loginpage
        # Универсальная обработка сообщений об ошибках (из УРЛ)
#        process_errors($Input, $data->{'Page'});
        # Поехали!
        my $handler = $AvaliableActions{$action}->{'handler'};
        if (not ref $handler and $handler =~ /^\*(.+)::[^:]+$/) {
            eval qq{ use $1; };
            dmp $@ if $@;
        }
        return $AvaliableActions{$action}->{'handler'}->($req, $data, $postargs);
    } else {
        return MordaX::Output::notfound($req);
    }
}

sub handle_my_parse {
    my ($req, $data, $postargs) = @_;

    my $p = $data->{'Page'};
    $p->{'my_cookie'} = $req->{'Getargshash'}->{'my'} || $postargs->{'my'} || $req->{'Cookies'}->value('my');
    if ($p->{'my_cookie'}) {
        $p->{'my_array'}  = MordaX::My::unmarshal($p->{'my_cookie'});
        $p->{'my_parsed'} = MordaX::My::PervertSetup($p->{'my_array'});
        $p->{'my_parsed'} = JSON::XS->new->canonical(1)->pretty(1)->allow_unknown(1)->encode($p->{'my_parsed'});
        $p->{'my_array'}  = JSON::XS->new->canonical(1)->pretty(1)->allow_unknown(1)->encode($p->{'my_array'});
    }

    return resp($req, 'test/test_my_parse.html', $data);
}

sub handle_id_slot {
    my ($req, $data, $postargs) = @_;

    my $p = $data->{Page};
    $p->{id} = $req->{Getargshash}{id} || $postargs->{id};
    for my $id (split /[,;]+/, $p->{id}) {
        push @{$p->{id_array}}, {
            id => $id,
            common_slot => MordaX::Experiment::AB::Helper::make_common_slot($id),
            salted_slot => MordaX::Experiment::AB::Helper::make_salted_slot($id),
        }
    }
    $p->{id_array} = [sort {$a->{common_slot} <=> $b->{common_slot}} @{$p->{id_array}}];

    return resp($req, 'test/test_id_slot.html', $data);
}

# DEPRECATED:
sub handle_megafon {
    my ($req, $data) = @_;

    my $megafon_headers = {
#    'X-MEGAFON-CI'  => '0122',
#    'X-MEGAFON-LAC' => '1E38',
# LAC:
# X-MEGAFON-SAC -- WCDMA (3G)
# X-MEGAFON-LAC -- GSM
# CI:
# X-MEGAFON-LAC
        'CI'  => $req->{'UserHeaders'}->{'X-MEGAFON-CI'},
        'LAC' => $req->{'UserHeaders'}->{'X-MEGAFON-LAC'},
        'SAC' => $req->{'UserHeaders'}->{'X-MEGAFON-SAC'},
    };
    my $megafon_data = {
        'lac' => $megafon_headers->{'SAC'} || $megafon_headers->{'LAC'},
        'ci' => $megafon_headers->{'CI'},
    };

    $data->{'Page'}->{'megafon_headers'} = $megafon_headers;

    if (!$megafon_data->{'ci'} || !$megafon_data->{'lac'}) {
        $data->{'Page'}->{'success'} = 0;
        return resp($req, 'test_megafon.html', $data);
    }
    $data->{'Page'}->{'success'} = 1;

    my $ua = MP::UserAgent->new('follow_redirects' => 0);

# 2 -- Megafon
# 250 -- city id
# -90 -- signal power?
    my $param =
      join('&', 'version=1', 'cellid=' . join(',', 250, 2, hex($megafon_data->{'ci'}), hex($megafon_data->{'lac'}), -90), 'usedb=cellid');

    # Getting XML with coordinates
    my $url_xml = 'http://api.lbs.mobile.maps.yandex.net/getlocation?geolocation=' . encode_base64($param);
    my $resp    = $ua->get($url_xml);
    my $xml     = $resp->content();

    # Gettong autogenerated link for image to static-maps(from Location header)
    my $url_redirect_img = $url_xml . '&url=http%3A%2F%2Fstatic-maps.yandex.ru%2F1.x%2F';
    $resp = $ua->get($url_redirect_img);
    my $location_img = $resp->headers()->{'location'};

    # Gettong autogenerated link to maps(from Location header)
    my $url_redirect_map = $url_xml . '&url=http%3A%2F%2Fm.maps.yandex.ru%2F';
    $resp = $ua->get($url_redirect_map);
    my $location_map = $resp->headers()->{'location'};

    $data->{'Page'}->{'location_img'} = $location_img;
    $data->{'Page'}->{'param'}        = $param;
    $data->{'Page'}->{'url_xml'}      = $url_xml;
    $data->{'Page'}->{'location_map'} = $location_map;
    $data->{'Page'}->{'xml'}          = $xml;

    return resp($req, 'test_megafon.html', $data);
}
# END DEPRECATED

sub handle_headers {
    my ($req, $data) = @_;

    my $cont = Data::Dumper->Dump([$req->{'UserHeaders'}], ['headers'],);
    my $output = '<html><head><title></title></head><body><pre>' . $cont . "</pre></body></html>\n";
    return MordaX::Output::respond($req, $output, [], 'text/html');
}

sub handle_geo {
    my ($req, $data) = @_;

    my $args = $req->{'Getargshash'};
    my $page = $data->{'Page'};
    if ($args->{fromcookies}) {
        $page->{ip}  = $req->{'X-Forwarded-For'} || $req->{'RemoteIp'};
        $page->{gid} = $req->{yandex_gid};
        $page->{ys}  = $req->{'Cookies'}->{ys};
        $page->{yp}  = $req->{'Cookies'}->{yp};
    } else {
        #from FORM FILEDS
        for (qw/ip gid yp ys/) {
            if ($args->{$_}) {
                #if($args->{$_} =~/\%\w\w/){
                #} else {
                #double unescape
                $page->{$_} = URI::Escape::XS::uri_unescape($args->{$_});
                #}
            }
        }
    }
    for (qw/yp ys/) {
        #.gpauto.55_78916850538931:38_0926164239645:300:1:1327330173
        my $time = time;
        if ($page->{$_} =~ m/gpauto\.\-?\d+_\d+/) {
            $page->{$_} =~ s/(gpauto\.[^:]*?:[^:]*:[^:]*:[^:]*:)\d+?(#.*)?$/$1$time$2/g;
            #logit('debug', "MODIFIED:" . $page->{$_} );
        }
    }
    my %decode_attr;
    for (qw/ip gid yp ys/) {
        $decode_attr{$_} = $page->{$_};
    }
    for my $key (qw/gid/) {
        my $val = $page->{$key};
        my $name = geo($val, 'name');
        utf8::decode($name);
        if ($val and $name) {
            $page->{$key . '_decoded'} = $name;
        }
    }
    #decode!
    use Geo;
    use Data::Dumper;
    my $result = Geo::get_geo_code_core(%decode_attr);
    dmp($result);

    if ($page->{gid}) {
        $result->{gid} = $page->{gid};
    }
    $page->{result} = $result;
    for my $key (qw/suspected_region gid region region_by_ip/) {
        my $val = $result->{$key};
        if ($val and $val > 0) {
            my $name = geo($val, 'name');
            if ($name) {
                $result->{$key . '_decoded'} = $name;
                utf8::decode($result->{$key . '_decoded'});
            }
        }

    }
    $page->{result_json} = JSON::XS->new->canonical(1)->utf8(0)->pretty(1)->encode($result);

    $page->{time}      = time();
    $page->{yu}        = $req->{'yu'};
    $page->{sk}        = $req->{'sk'};
    $page->{yandexuid} = $req->{'yandex_uid'};
#    warn Dumper($result);
#    warn Dumper($data);

    return resp($req, 'test_geo.html', $data);

}

sub handle_geo_ip_search {
    my ($req, $data) = @_;
    my $args     = $req->{'Getargshash'};
    my $gid      = $args->{gid};
    my $format   = $args->{format};
    my $gid_name = geo($gid, 'name');

    my $ip = '';
    if ($gid_name) {
        #use lib::abs qw(../t/testlib/);
        #require testlib::GeoHelper;
        my $gh = testlib::GeoHelper->new('fast' => 1);
        $ip = $gh->ip($gid);
    }

    if ($format eq 'json') {
        $data->{JSON} = {
            "gid"  => $gid,
            "name" => $gid_name,
            "ip"   => $ip,
        };
        utf8::decode($data->{JSON}->{'name'}) unless utf8::is_utf8($data->{JSON}->{'name'});
        return jsonresp($req, $data);
    }

    my $output = "gid: $gid
name:$gid_name
ip: $ip";

    return MordaX::Output::respond($req, $output, undef, 'text/plain');
}

my %whitelist = (
    '1669235992' => 'moikrug.ru',
    '3950101'    => 'video.yandex.ru',
    '1369123854' => 'gorod.yandex.ru',
    '1699062299' => 'sprav.yandex.ru',
    '37880333'   => 'direct.yandex.ru',
    '1105616640' => 'money.yandex.ru',
    '618474752'  => 'rasp.yandex.ru',
    '1442027534' => 'translate.yandex.ru',
    '1291839232' => 'people.yandex.ru',
    '142201088'  => 'metrika.yandex.ru',
    '1102174725' => 'blogs.yandex.ru',
    '1169856256' => 'blogs.yandex.ru',
    '828684288'  => 'moikrug.ru',
    '1446123777' => 'partner.yandex.ru',
    '692481029'  => 'ege.yandex.ru',
    '219513089'  => 'yaca.yandex.ru',
    '988107776'  => 'yaca.yandex.ru',
    '1060057624' => 'calendar.yandex.ru',
    '1141539328' => 'blogs.yandex.ru',
    '135675136'  => 'video.yandex.ru',
    '1554438913' => 'webmaster.yandex.ru',
    '203652881'  => 'money.yandex.ru',
    '1577178889' => 'avia.yandex.ru',
    '1349584640' => 'time.yandex.ru',
    '2040688131' => 'gorod.yandex.ru',
    '961629696'  => 'images.yandex.ru',
    '1858824969' => 'time.yandex.ru',
    '641904640'  => 'yaca.yandex.ru',
    '568374784'  => 'music.yandex.ru',
    '2127857408' => 'images.yandex.ru',
    '205239040'  => 'slovari.yandex.ru',
    '1266813697' => 'money.yandex.ru',
    '1222878215' => 'avia.yandex.ru',
    '1453242370' => 'realty.yandex.ru',
    '1120642817' => 'people.yandex.ru',
    '1692444673' => 'fotki.yandex.ru',
    '391814164'  => 'rabota.yandex.ru',
    '2018792449' => 'video.yandex.ru',
    '598788875'  => 'internet.yandex.ru',
    '1562422788' => 'sprav.yandex.ru',
    '296526083'  => 'webmaster.yandex.ru',
    '322631168'  => 'fotki.yandex.ru',
    '1328514048' => 'images.yandex.ru',
    '1678526724' => 'gorod.yandex.ru',
    '742100481'  => 'disk.yandex.ru'
);

sub handle_sites {
    my ($req, $data) = @_;
    MordaX::Data_load::init_datas();

    my @headers = ({
            'name'  => 'Cookie',
            'value' => 'yandexuid=' . $req->{'yandexuid'},
        },
    );
    my $http_agent = MordaX::HTTP->new($req);
    $http_agent->add(
        'alias'   => 'yabs_sites',
        'url'     => 'http://yabs.yandex.ru/bigb?operation=6',
        'timeout' => 2,
        'retries' => 2,
        'can_v6'  => 1,
        'headers' => \@headers,
    );
    my $yabs_json = $http_agent->result_req_info('yabs_sites')->{response_content};
    my $yabs_data = JSON::XS::decode_json($yabs_json);

    my %yandex_services;
    my %id2service;    # Service can have many ids
    foreach my $record (@{MordaX::Data_get::get_static_data($req, 'services_yandex', all => 1)}) {
        $yandex_services{$record->{name}} = $record;
        foreach my $id (split /,/, $record->{id}) {
            $id2service{$id} = $record->{name};
        }
    }

    $data->{Page}{Whitelist} = \%yandex_services;

    my @sites;

    foreach my $site (grep { $_->{id} == 326 } @{$yabs_data->{data}->[0]->{segment}}) {
        foreach my $tuple (split(/,/, $site->{value})) {
            my %site;
            my @vals = split /:/, $tuple;

            next unless ($id2service{$vals[0]});    # Skip site if it isn't in whitelist
            my $name = $id2service{$vals[0]};

            $site{id}              = $vals[0];
            $site{days}            = $vals[1];
            $site{hits}            = $vals[2];
            $site{name}            = $name;
            $site{weight}          = $yandex_services{$name}->{weight};
            $site{weight_adjusted} = $site{hits} * $site{weight} * $site{days};

            push @sites, \%site;
        }
    }

    $data->{Page}{Hits} = [sort { $b->{weight_adjusted} <=> $a->{weight_adjusted} } @sites];

    my @external_sites;
    my @external_sites_whitelist;
    my %external_id2site;
    foreach my $record (@{MordaX::Data_get::get_static_data($req, 'services_external', all => 1)}) {
        foreach my $id (split /,/, $record->{id}) {
            $external_id2site{$id} = {%$record};
            $external_id2site{$id}->{id} = $id;
        }
    }
    foreach my $record (grep { $_->{id} == 198 } @{$yabs_data->{data}->[0]->{segment}}) {
        foreach my $id (split(/,/, $record->{value})) {
            push @external_sites, $id;
            push @external_sites_whitelist, $external_id2site{$id} if ($external_id2site{$id});
        }
    }

    $data->{Page}{ExternalSites}          = \@external_sites;
    $data->{Page}{ExternalSitesWhitelist} = \@external_sites_whitelist;

    return resp($req, 'testsites.html', $data)

}

sub handle_interests {
    my ($req, $data) = @_;

    # Process banners
    my $banners = MordaX::Banners->new($req);
    # Collect banners from multiplexed request
    $banners->download($req, 'only' => 'yabs');
    $banners->serialize_yabs($req, $data->{'Page'});

    my $tinfo = $banners->{'TargetingInfo'};
    if ($req->{'yandexuid'}) {
        my $logstring = join(':', 'yandexuid', $req->{'yandexuid'});
        for (qw{yob gender category}) {
            if (UNIVERSAL::isa($tinfo->{$_}, 'ARRAY')) {
                $logstring .= "\t" . join(':', $_, join(',', @{$tinfo->{$_}}));
            } else {
                $logstring .= "\t" . join(':', $_, (defined $tinfo->{$_} ? $tinfo->{$_} : ''));
            }
        }
        logit('warning', 'themetarget: ' . $logstring);
    }

    return resp($req, 'testinterests.html', $data);
}

sub HelloWorld {
    my ($req, $data) = @_;

    my $p = $data->{'Page'};

    MordaX::Input::input_yandexuid(undef, $req);

    if ($req->{'MordaContent'} eq 'big') {
        if ($req->{'MordaZone'} eq 'ua') {
            $p->{'Hypostasis'} = 'big-ua';
        } elsif ($req->{'MordaZone'} eq 'by') {
            $p->{'Hypostasis'} = 'big-by';
        } elsif ($req->{'MordaZone'} eq 'kz') {
            $p->{'Hypostasis'} = 'big-kz';
        } else {
            $p->{'Hypostasis'} = 'big-ru';
        }
    } elsif ($req->{'Family'}) {
        $p->{'Hypostasis'} = 'big-family';
    } elsif ($req->{'MordaContent'} eq 'com') {
        $p->{'Hypostasis'} = 'com';
    } elsif (($req->{'MordaContent'} eq 'mob') || ($req->{'MordaContent'} eq 'touch')) {
        $p->{'Hypostasis'} = 'mob-ru';
    } elsif ($req->{'MordaContent'} eq 'tel') {
        $p->{'Hypostasis'} = 'tel-ru';
    } elsif ($req->{'MordaContent'} eq 'mobyaru') {
        $p->{'Hypostasis'} = 'mobyaru';
    } else {
        $p->{'Hypostasis'} = 'big-ru';
    }

    $p->{'Cookies'} = [];
    for (sort keys %{$req->{'Cookies'}}) {
        push @{$p->{'Cookies'}}, {
            'name'  => $_,
            'value' => $req->{'Cookies'}->{$_}
        };
    }
    $p->{'yu'} = $req->{'yu'};
    for my $sktype ('u', 'y', '_') {
        next if ($sktype eq 'u' && !$req->{'UID'});
        $p->{"sk_${sktype}_now"}       = MordaX::Utils::sk_gen($req, 0,  $sktype);
        $p->{"sk_${sktype}_yesterday"} = MordaX::Utils::sk_gen($req, -1, $sktype);
    }

    return resp($req, 'test/index.html', $data);
}

sub Dummy {
    my ($req, $data) = @_;

    return MordaX::Output::respond($req, '<html><head><title>Яндекс</title></head><body>Dummy&nbsp;</body></html>',
        $data->{'cookies'}, $data->{'content-type'});
}

sub yandexuid_cookie_age {
    my ($req, $data, $postargs) = @_;

    my $p = $data->{'Page'};

    my $yandexuid = $postargs->{'yandexuid'} || $req->{'yandexuid'};
    my $parsed = Yandexuid::parse_to_hash($yandexuid);
    $parsed->{'dt'} = MP::Time::strftime_ts("%F %T", $parsed->{'ts'});

    my $json_text = JSON::XS->new->pretty(1)->canonical(1)->encode($parsed);

    $p->{'yandexuid'} = $yandexuid;
    $p->{'json_text'} = $json_text;

    return resp($req, 'test/yandexuid_get.html', $data);
}

sub yandexuid_cookie_set {
    my ($req, $data, $postargs) = @_;

    my $p = $data->{'Page'};

    my $new_yandexuid = $p->{'new_yandexuid'} = $postargs->{'yandexuid'};
    my $yandexuid     = $p->{'yandexuid'} = $req->{'yandexuid'};
    my $oldyandexuid  = 0;
    my $yudate        = undef;
    if ($yandexuid =~ /^(\d+)(\d{10})$/o) {
        my ($sec, $min, $hour, $mday, $mon, $year) = localtime($2);
        $yudate = sprintf("(%02d/%02d/%04d %02d:%02d:%02d)", $mday, $mon + 1, $year + 1900, $hour, $min, $sec);
        $oldyandexuid = sprintf('%d%d', $1, ($req->{'time'} - 345600));    # Состарить на 4 суток. 4 * 24 * 3600
    } else {
        $oldyandexuid = substr(int(rand(1000000000)), 0, 19 - length($req->{'time'})) . ($req->{'time'} - 345600);
    }
    $p->{'yudate'} = $yudate;
    $p->{'oldyandexuid'} = $oldyandexuid;

    my @cookies;
    my $yandexdomain = '.yandex.ru';
    if ($req->{'Domain'} eq 'yandex.com') {
        $yandexdomain = '.yandex.com';
    } elsif ($req->{'Domain'} eq 'yandex.com.tr') {
        $yandexdomain = '.yandex.com.tr';
    }

    if ($postargs->{mode} eq 'set' && $new_yandexuid =~ /^\d+$/) {
        push @cookies,
          MordaX::Cookie->new(
            $req,
            -name    => 'yandexuid',
            -value   => $new_yandexuid,
            -path    => '/',
            -secure  => 0,
            -expires => '+10y',
            -domain  => $yandexdomain,
          );
        $p->{'new_yandexuid'} = $new_yandexuid;
    } elsif ($postargs->{mode} eq 'gen') {
        my $_uids = _generate_yandexuid_for_salt($req, $postargs);
        $p->{'generated_yandexuid_cont'} = join('<br/>', @$_uids);
    }
    $p->{'salt'} = $postargs->{salt} || MordaX::Experiment::AB::Helper::get_salt_for_yandexuid();
    $p->{'slot'} = $postargs->{slot};
    $p->{'percent'} = $postargs->{percent};
    $p->{'ancient'} = $postargs->{ancient} ? "checked" : q();

    $data->{'cookies'} = \@cookies;

    return resp($req, 'test/yandexuid_set.html', $data);
}

sub _generate_yandexuid_for_salt {
    my ($req, $args) = @_;
    my $values = [];
    if (defined $args->{slot} && $args->{percent} && $args->{salt}) {
        my $slot_from = $args->{slot};
        my $slot_to   = MordaX::Experiment::_get_exp_slot_to($args->{slot}, $args->{percent});
        my $max_retry = 100;
        my $time      = $req->{time};
        $time -= 4 * 24 * 3600 if $args->{ancient};    # делаем 4-дневную куку
                                                       # максимум будет 100 попыток подбора
        for (my $i = 0; $i < $max_retry; $i++) {
            my $req_local = MordaX::Req->new();
            $req_local->{time} = $time;
            my $yu          = Yandexuid::gen_new_value($req_local);
            my $salted_slot = MordaX::Experiment::AB::Helper::make_salted_slot($yu);
            if ($salted_slot >= $slot_from && $salted_slot <= $slot_to) {
                push @$values, $yu;
            }
            last if scalar @$values == 5;
        }
    }
    return $values;
}

sub set_sessionid {
    my ($req, $data, $postargs) = @_;
    my $new = $postargs->{'Session_id'};
    my $now = $req->{'Session_id'};
    my @cookies;
    my $yandexdomain = '.yandex.ru';
    if ($req->{'Domain'} ~~ ['yandex.com', 'yandex.com.tr']) {
        $yandexdomain = '.' . $req->{'Domain'};
    }
    my $cont = "<br/>Session_id cookie: $now ";
    if (defined $new) {
        push @cookies,
          MordaX::Cookie->new(
            $req,
            -name    => 'Session_id',
            -value   => $new,
            -path    => '/',
            -secure  => 0,
            -expires => '+10y',
            -domain  => $yandexdomain,
          );
        $cont .= "<br/>Session_id cookie SET: $new";
    }

    my $output = qq{<html><head><title></title></head><body><br/>
$cont
<form method=POST>
<input name=Session_id value="$now">
<input type=submit>
</form>

</body></html>\n};
    return MordaX::Output::respond($req, $output, \@cookies, 'text/html');
}

sub set_yandex_gid_cookie {
    my ($req, $data, $postargs) = @_;

    my $s_gid          = $req->{'Getargshash'}->{'gid'} || '';
    my $new_yandex_gid = $postargs->{'yandex_gid'};
    my $yandex_gid     = $req->{'yandex_gid'};

    my @cookies;
    my $cont = "<br/>yandex_gid cookie: $yandex_gid";
    if ($new_yandex_gid && $new_yandex_gid =~ /^\d+$/) {
        push @cookies,
          MordaX::Cookie->new(
            $req,
            -name    => 'yandex_gid',
            -value   => $new_yandex_gid,
            -path    => '/',
            -secure  => 0,
            -expires => '+10y',
            -domain  => '.' . $req->{'Domain'},
          );
        $cont .= "<br/>yandex_gid cookie SET: $new_yandex_gid";
    }
    $cont .= qq{
<br/>
<form method=POST>
<input name=yandex_gid value="$s_gid">
<input type=submit>
<a href="http://www-rcm.yandex.ru">rcm</a>
</form>
};

    my $output = '<html><head><title></title></head><body>' . $cont . "</body></html>\n";
    return MordaX::Output::respond($req, $output, \@cookies, 'text/html');
}

sub SetWCookie {
    my ($req, $data) = @_;

    my $table = $req->{'Getargshash'}->{'block'};
    my $pid   = $req->{'Getargshash'}->{'pid'};
    my $hpid  = $req->{'Getargshash'}->{'hpid'};
    my $row   = $req->{'Getargshash'}->{'row'};
    my $temp  = $req->{'Getargshash'}->{'temp'};

    my $redirme = true($req->{'Getargshash'}->{'redirme'}) ? 1 : 0;

    my $ws = WBOX::Storage->new();

    $data->{'JSON'} = {
        'error' => '',
        'state' => 0,
        'ncrnd' => $data->{'Page'}->{'NcRnd'},
    };

    # Умная расстановка приоритетов
    if ($pid) {
        if ($row && $table) {    # Указали всё, надо проверить, что обновили
            if ($hpid && ($pid eq $hpid)) {
                $pid = undef;
            } else {
                $row   = undef;
                $table = undef;
            }
        } elsif ($row) {         # Это просто мусор
            $row = undef;
        } elsif ($table) {
            $table = undef;
        }
    }

    if ($pid) {
        my ($blockid, $cleanpid) = WBOX::Utils::GetBlockID(undef, $pid, undef);    # Just for check
        if ($cleanpid) {
            $cleanpid = $ws->unpackID($cleanpid);                                  # Just for check too
        }
        if ($blockid && $cleanpid) {
            my $wcookievalue = wcookievalue($req, $pid, $temp ? 1 : undef);
            if ($wcookievalue) {
                push @{$data->{'cookies'}}, $wcookievalue;
                $data->{'JSON'}->{'state'} = 1;
            } else {
                $data->{'JSON'} = {
                    'state' => 0,
                    'error' => 'Ошибка загрузки паттерна',
                    'ncrnd' => $data->{'Page'}{'NcRnd'},
                };
            }
        } else {
            $data->{'JSON'} = {
                'state' => 0,
                'error' => 'Недопустимое значение pid',
                'ncrnd' => $data->{'Page'}->{'NcRnd'},
            };
        }
    } else {
        if ($table && $row) {
            my $packedrow = $ws->packID($row);
            if ($packedrow) {
                $pid = $table . $packedrow;
                my $wcookievalue = wcookievalue($req, $pid, $temp ? 1 : undef);
                if ($wcookievalue) {
                    push @{$data->{'cookies'}}, $wcookievalue;
                    $data->{'JSON'}->{'state'} = 1;
                } else {
                    $data->{'JSON'} = {
                        'state' => 0,
                        'error' => 'Ошибка загрузки паттерна',
                        'ncrnd' => $data->{'Page'}{'NcRnd'},
                    };
                }
            } else {
                $data->{'JSON'} = {
                    'state' => 0,
                    'error' => 'Недопустимое значение row',
                    'ncrnd' => $data->{'Page'}->{'NcRnd'},
                };
            }
        } else {
            $data->{'JSON'} = {
                'state' => 0,
                'error' => 'Надо указать pid или block и row',
                'ncrnd' => $data->{'Page'}->{'NcRnd'},
            };
        }
    }
    if ($redirme) {
        my $path = true($req->{'Getargshash'}{'dumpw'}) ? '/?dumpw=yes' : '/';
        return MordaX::Output::redirect($req, $path, $data->{'cookies'}, $data->{'content-type'});
    } else {
        return iframeresp($req, $data, 'updatewcooke');
    }
}

sub wcookievalue {
    my ($req, $pid, $temp) = @_;

    my $container = MordaX::Widgets::Utils::container($req);
    return undef unless (defined($container));

    my $wss = WBOX::Storage::WSettings->new();
    my ($pattern, $error) = $wss->simplegetpattern({
            'project'   => 1,
            'container' => $container,
            'page'      => 0,
            'pid'       => $pid,
        }
    );

    unless ($pattern) {
        logit('error', sprintf('Failed to get pattern %s: %s', $pid, $error));
        return undef;
    }

    my $wauth = WBOX::Wauth::gen(1, $container, $pid, undef, undef, undef, $pattern->salt());

    $wauth = '*' . $wauth if ($temp);

    return MordaX::Cookie->new(
        $req,
        -name    => 'w',
        -value   => URI::Escape::XS::uri_escape($wauth),
        -path    => '/',
        -secure  => 0,
        -expires => '+10y',
    );

}

sub ShowWCookie {
    my ($req, $data) = @_;

    my $patternid  = $req->{'patternid'};
    my $hpatternid = $req->{'hiddenpatternid'};
    my $temp       = undef;

    if ($hpatternid && !$patternid) {
        $patternid = $hpatternid;
        $temp      = 1;
    }

    $data->{'JSON'} = {
        'error' => '',
        'pid'   => '',
        'block' => '',
        'row'   => '',
        'temp'  => 'no',
        'ncrnd' => $data->{'Page'}->{'NcRnd'},
    };

    if ($patternid) {
        my ($blockid, $cleanpid) = WBOX::Utils::GetBlockID(undef, $patternid, undef);

        if ($cleanpid) {
            my $ws = WBOX::Storage->new();
            $cleanpid = $ws->unpackID($cleanpid);
        }

        if ($blockid && $cleanpid) {
            $data->{'JSON'}->{'pid'}   = $patternid;
            $data->{'JSON'}->{'block'} = $blockid;
            $data->{'JSON'}->{'row'}   = $cleanpid;
            $data->{'JSON'}->{'temp'}  = $temp ? 'yes' : 'no';
            $data->{'JSON'}->{'sql'} =
              'SELECT * FROM patterns_'
              . $blockid
              . " WHERE pid='$cleanpid'; SELECT * FROM instances_"
              . $blockid
              . " WHERE pid='$cleanpid'; SELECT * FROM isettings_"
              . $blockid
              . " WHERE pid='$cleanpid';";
        } else {
            $data->{'JSON'}->{'error'} = 'Странное значение pid в куке w';
        }
    } else {
        $data->{'JSON'}->{'error'} = 'Нет валидной куки w';
    }

    return jsresp($req, $data, 'drawwcookievals');
}

sub Subscription {
    my ($req, $data) = @_;

    my $container = MordaX::Widgets::Utils::container($req);
    unless (defined($container)) {
        $data->{'JSON'} = {'error' => 'UNSUPPORTED',};
        return jsresp($req, $data, 'drawsubscr');
    }

    my $auth = $req->{'AuthOBJ'};
    $data->{'JSON'} = {
        'container' => $container,
        'error'     => '',
    };

    if (defined($auth) && $auth->{'AuthState'} && ($auth->{'AuthState'} eq 'AUTH')) {
        $data->{'JSON'}->{'logged'} = '1';
        $data->{'JSON'}->{'login'}  = $auth->{'INFO'}->{'login'};
        my $subscription = $auth->Subscription($container);
        if (defined($subscription) && ($subscription =~ /^[012]$/o)) {
            $data->{'JSON'}->{'subscription'} = $subscription;
        } else {
            $data->{'JSON'}->{'subscription'} = undef;
            $data->{'JSON'}->{'error'}        = 'Ошибка получения информации о подписке';
        }
        my $wboxrv = WBOX::Wbox::GetAll(
            'project'     => 1,
            'container'   => $container,
            'patternpage' => 0,
            'ouid'        => $auth->{'UID'},
            'Request'     => $req,
            'object'      => 1,
            'light'       => 1,
        );
        if (UNIVERSAL::isa($wboxrv, 'HASH') && $wboxrv->{'ok'} && defined(my $pattern = $wboxrv->{'patternobj'})) {
            my $patternid = $pattern->id();
            my ($blockid, $cleanpid) = WBOX::Utils::GetBlockID(undef, $patternid, undef);

            if ($cleanpid) {
                my $ws = WBOX::Storage->new();
                $cleanpid = $ws->unpackID($cleanpid);
            }
            $data->{'JSON'}->{'pid'}   = $patternid;
            $data->{'JSON'}->{'block'} = $blockid;
            $data->{'JSON'}->{'row'}   = $cleanpid;
            $data->{'JSON'}->{'temp'}  = $pattern->temp() ? 'yes' : 'no';
            $data->{'JSON'}->{'sql'} =
              'SELECT * FROM patterns_'
              . $blockid
              . " WHERE pid='$cleanpid'; SELECT * FROM instances_"
              . $blockid
              . " WHERE pid='$cleanpid'; SELECT * FROM isettings_"
              . $blockid
              . " WHERE pid='$cleanpid';";
        } else {
            $data->{'JSON'}->{'pid'}   = '-';
            $data->{'JSON'}->{'block'} = '-';
            $data->{'JSON'}->{'row'}   = '-';
            $data->{'JSON'}->{'temp'}  = '-';
            $data->{'JSON'}->{'sql'}   = '-';
        }
    } else {
        $data->{'JSON'}->{'logged'} = 0;
    }

    return jsresp($req, $data, 'drawsubscr');
}

sub Subscribe {
    my ($req, $data) = @_;

    my $container = MordaX::Widgets::Utils::container($req);
    unless (defined($container)) {
        $data->{'JSON'} = {'error' => 'Виджеты не поддерживаются',};
        return iframeresp($req, $data, 'subscribe');
    }

    my $auth = $req->{'AuthOBJ'};
    $data->{'JSON'} = {
        'container' => $container,
        'error'     => '',
        'state'     => 0,
    };

    if (defined($auth) && $auth->{'AuthState'} && ($auth->{'AuthState'} eq 'AUTH')) {
        $data->{'JSON'}->{'logged'} = 1;

        my $rc  = undef;
        my $way = $req->{'Getargshash'}->{'subscr'};

        if (defined($way) && ($way =~ /^[012]$/o)) {
            if ($way eq '0') {
                $rc = $auth->DropWidgets($req, $container);
            } elsif ($way eq '1') {
                $rc = $auth->EnableWidgets($req, $container);
            } else {
                $rc = $auth->SuppressWidgets($req, $container);
            }
            if ($rc) {
                $data->{'JSON'}->{'state'}      = 1;
                $data->{'JSON'}->{'lastupdate'} = sprintf(
                    '%02d/%02d/%04d %02d:%02d:%02d',
                    $req->{'LocalDay'},
                    $req->{'LocalMon'},
                    $req->{'LocalYear'},
                    $req->{'LocalHour'},
                    $req->{'LocalMin'},
                    $req->{'LocalSec'}
                );
            } else {
                $data->{'JSON'}->{'state'} = 0;
                $data->{'JSON'}->{'error'} = 'Ошибка обновления подписки';
            }
        } else {
            $data->{'JSON'}->{'error'} = 'Недопустимое значение подписки';
        }
    } else {
        $data->{'JSON'}->{'logged'} = 0;
        $data->{'JSON'}->{'error'}  = 'Пожалуйста, залогиньтесь';
    }

    return iframeresp($req, $data, 'subscribe');
}

sub process_errors {

}

sub resp {
    my ($req, $templatename, $data) = @_;

    $data->{'Page'}{'DumpVariables'} = $req->{'DumpVariables'};
    my $output = '';
    my $rc = $MordaX::Tmpl::tt->process($templatename, $data->{'Page'}, \$output, binmode => ':utf8');
    unless ($rc) {
        my $err = 'Template parsing error: ' . $MordaX::Tmpl::tt->error();
        #logit('interr', $err);
        $output = '<html><head><title>Template error</title></head><body>' . $err . "</body></html>\n";
    }

    MordaX::CSP::instance($req)->off();

    return MordaX::Output::respond($req, $output, $data->{'cookies'}, $data->{'content-type'});
}

sub iframeresp {
    my ($req, $data, $fname) = @_;

    my $jsoner = JSON::XS->new();

    my $iframe = $req->{'Getargshash'}->{'iframe'};

    if (defined($iframe) && ($iframe =~ /^(on|yes|true|1)$/io)) {
        $iframe = 1;
    } else {
        $iframe = undef;
    }

    my $output = '<html><head><title>Яндекс</title></head><body>';

    if ($iframe) {
        $output .=
          '<script type="text/javascript">parent.'
          . $fname . '('
          . $jsoner->encode($data->{'JSON'})
          . ');document.location=\'/test/dummy/\';</script>';
    } else {
        if (UNIVERSAL::isa($data->{'cookies'}, 'ARRAY') && scalar(@{$data->{'cookies'}})) {
            $output .= '<div>' . join('</div><div>', map { $_->as_string() } @{$data->{'cookies'}}) . '</div>';
        }
        $output .= '<div><a href="http://' . $req->{'HostName'} . '/">http://' . $req->{'HostName'} . '/</div>';
    }

    $output .= '</body></html>';
    $data->{'content-type'} = 'text/html';
    return MordaX::Output::respond($req, $output, $data->{'cookies'}, $data->{'content-type'});
}

sub jsresp {
    my ($req, $data, $fname) = @_;

    my $jsoner = JSON::XS->new();
    my $output = "$fname(" . $jsoner->encode($data->{'JSON'}) . ');';
    $data->{'content-type'} = 'text/javascript';
    return MordaX::Output::respond($req, $output, $data->{'cookies'}, $data->{'content-type'});
}

sub jsonresp {
    my ($req, $data, $fname) = @_;

    my $jsoner = JSON::XS->new();
    my $output = $jsoner->encode($data->{'JSON'});

    $data->{'content-type'} = 'text/javascript';
    return MordaX::Output::respond($req, $output, $data->{'cookies'}, $data->{'content-type'});
}

sub cookieobject {
    my ($cookievalue) = @_;

}

sub handle_ip {
    my ($req, $data) = @_;

    my @path;
    my $cont = '';
    $cont .= qq{
<br/>
<form method=GET>
<input name=ip>
<input type=submit>
</form>
};
    if ($req->{'Getargshash'}->{'ip'}) {
        my %attr = (ip => $req->{'Getargshash'}->{'ip'},);
        my $result = Geo::get_geo_code_core(%attr,);
        if ($result->{ok}) {
        }
        $cont .= '<pre>';
        $cont .= Data::Dumper->Dump([$result], ['GeobaseInfo'],);
        $cont .= "\npath: ";

        if ($result->{'region'}) {
            for ((reverse geo($result->{'region'}, 'parents')), $result->{'region'}) {
                next if $_ == 10000;
                next if $_ == 10001;
                push @path, geo($_, 'name') . '(' . $_ . ')';
            }
            $cont .= join '->', @path;
        }
        $cont .= "\n";
        $cont .= '</pre>';
    }

    if ($req->{'Getargshash'}->{'p'}) {
        my $output = join '->', @path;
        return MordaX::Output::respond($req, $output, [], 'text/plain');
    }

    my $output = '<html><head><title></title></head><body>' . $cont . "</body></html>\n";
    return MordaX::Output::respond($req, $output, [], 'text/html');
}

sub handle_lang {
    my ($req, $data) = @_;
    $data->{'content-type'} = 'text/html';
    my $to = '/tmp';
    $to .= '/Lang_auto.pm' . '.dev.' . $MordaX::Config::InstanceModifier;
    #my $to = lib::abs::path('../lib/MordaX');
    my $run    = lib::abs::path('../scripts') . "/get_lang.pl -t $to";
    my $output = qq{<pre>run: $run\nto: $to\n\n\n} . `$run`;
    #my $output = qq{<pre>run: $run\nto: $to\n\n\n};
    #$output .= '<br/>R:', system $run;
    my $headers = {};
    unless (-e $to) {
        $output .= 'Failed.<br/>';
        $headers->{'Status'} = '500 parse error';

    } else {
        $output .= qq{\nLoading:\n};
        #warn Dumper \%lang;
        #WARNING this is old style untested usage of Lang initializer
        #$output .= MordaX::Lang::reinit($to);
        #unlink $to;

        #$output .= qq{\nok.\n};
    }
    return MordaX::Output::respond($req, $output, $data->{'cookies'}, $data->{'content-type'}, $headers);

}

sub handle_harlog {
    my ($req, $data) = @_;

    my $uploads = $req->{'Uploads'};
    if ($uploads->{'har'} && $uploads->{'har'}->{'tempname'}) {
        my $har = `cat $uploads->{'har'}->{'tempname'}`;
        eval { $data->{'Page'}->{'har'} = JSON::XS::decode_json($har); };
        if ($@) {
            my $err = 'JSON error: ' . $@;
            $data->{'error'} = $err;
            logit('interr', $err);
        }
    }

    return resp($req, 'test_harlog.html', $data);
}

sub handle_phone {
    my ($req, $data) = @_;

    my $args = $req->{'Getargshash'};
    my $page = $data->{'Page'};

    if ($args->{useyours}) {
        dumpit('headers', $req->{UserHeaders});
        $args->{'user-agent'} = $req->{UserHeaders}->{'User-Agent'};
        $args->{'x-wap-profile'} = $req->{UserHeaders}->{'Wap-Profile'} || $req->{UserHeaders}->{'X-Wap-Profile'};
    }
    my $headers = {
        q{User-Agent}    => $args->{'user-agent'},
        q{X-Wap-Profile} => $args->{'x-wap-profile'},
    };

    my $host_name = "yandex.ru";

    if ($args->{'user-agent'} or $args->{'x-wap-profile'}) {
        #require MordaX::DetectDevice;
        my $detect_device = MordaX::DetectDevice->new();
        my $browser       = $detect_device->detect_browser_by_headers($headers);

        my $json = JSON::XS->new->pretty(1)->canonical(1)->encode({
                'browser' => $browser,
                #'apps_xml' => $applications,
            }
        );
        $page->{answer} = $json;
    }

    for ('user-agent', 'x-wap-profile') {
        $page->{$_} = $args->{$_};
    }

    return resp($req, 'test_phone.html', $data);

}

sub handle_form {
    my ($req, $data) = @_;

    return resp($req, 'test_form.html', $data);
}

sub handle_post {
    my ($req, $data) = @_;

    $data->{'Page'}{'dump'} = Data::Dumper->Dump([$req->{'UserHeaders'}], ['Headers']);

# Load POST body
    my $postfilename = $ENV{'REQUEST_BODY_FILE'};
    unless ($postfilename) {
        $data->{'Page'}{'state'} = 'No REQUEST_BODY_FILE ENV variable found';
        goto HANDLEPOSTRESP;
    }
    unless (-f $postfilename) {
        $data->{'Page'}{'state'} = "REQUEST_BODY_FILE $postfilename not found";
        goto HANDLEPOSTRESP;
    }
    my $rc = open my $postfh, "<", $postfilename;
    unless ($rc) {
        $data->{'Page'}{'state'} = "Failed to open REQUEST_BODY_FILE $postfilename: $!";
        goto HANDLEPOSTRESP;
    }
    local $/ = undef;
    my $postfilebody = <$postfh>;
    close $postfh;

    $data->{'Page'}{'postcontent'} = $postfilebody;
    $data->{'Page'}{'state'} = length($postfilebody) ? "loaded from $postfilename" : 'empty file';

  HANDLEPOSTRESP:
    return resp($req, 'test_post.html', $data);
}

sub handle_log {
    my ($req, $data) = @_;
    my $output = join(' ', map {"$_=$req->{'Getargshash'}{$_}\t"} sort keys %{$req->{'Getargshash'} || {}}) . "\n";
    Pfile::PWrite('getlog', $req->{'server_yyyymmdd'}, $output);
    return MordaX::Output::respond($req, $output, [], 'text/plain');
}

sub handle_302 {
    my ($req, $data) = @_;
    return MordaX::Output::redirect($req, '/test/geo#sync_cookie');
}

sub handle_version {
    my ($req, $data) = @_;

    my $instances = {
        dev31 => 1,
        dev46 => 1,
    };

    my $base       = lib::abs::path('..');
    my $changefile = lib::abs::path('../debian/changelog');
    my $changelog  = qx{head $changefile -n 40};
    utf8::decode($changelog);
    my $version;
    if ($changelog =~ /([\w-]+\s*\(.*?\))/) {
        $version = $1;
    } else {
        $version = "?";
    }
    my $page = $data->{Page};
    $page->{version}   = $version;
    $page->{changelog} = $changelog;
    $page->{instances} = [grep { -d "/opt/www/morda-$_" } keys %$instances];
    #logit('debug', "Ch: $changelog, $version");

    #
    #remote versions
    #
    my $versions_txt = qx/cd $base; git fetch ; git branch -r | grep zpackage/;
    my @versions     = ();
    while ($versions_txt =~ m{origin/zpackage\.(.*?)$}gm) {
        unshift @versions, $1;
    }
    $page->{versions} = ['dev', 'release', @versions[0 .. 10]];

    #grab current version

    return resp($req, 'test_version.html', $data);
}

sub handle_package {
    my ($req, $data) = @_;
    my $out = `dpkg -l | grep portal-morda`;
    return MordaX::Output::respond($req, $out, [], 'text/plain',);
}

sub handle_install_version {
    my ($req, $data) = @_;

    my $where;
    my $error;

    my $args     = $req->{'Getargshash'};
    my $version  = $args->{version};
    my $instance = $args->{instance};

    if ($instance =~ /^dev\d\d$/) {
        $where = $instance;
    } else {
        $error = "Not valid instance: $instance";
    }

    if ($where and not -d '/opt/www/morda-' . $where) {
        $error = "Instance Dir Not found";
        $where = undef;
    }

    logit('debug', "installl version : $version to $where");
    unless ($error) {

        my $jobs = MordaX::Cache->get('git_installer_jobs') || {};
        $jobs->{$where} = {
            version => $version,
            #path    => $path,
            where => $where,
        };
        unless (MordaX::Cache->set('git_installer_jobs', $jobs, 300)) {
            $error = "memd set error";
        }
    }

    $data->{'JSON'} = {
        version  => $version,
        instance => $instance,
        where    => $where,
        status   => $error ? 'error' : 'ok',
        error    => $error,
    };
    return jsonresp($req, $data);
}

sub handle_install_status {
    my ($req, $data) = @_;
    my $args     = $req->{'Getargshash'};
    my $instance = $args->{instance};

    logit('debug', 'install status');
    my $m = MordaX::Cache->new();
    my $path = lib::abs::path('.');
    $path =~ /morda-(dev\d{2})/;
    my $where = $instance;
    my $state = $m->get("gi_" . $where . '_state') || {};

    $state->{instance} = $instance;
    my $tail = $state->{log};
    $tail =~ s/[\s\S]*?(([^\n]*\n){19})([^\n]+)?$/$1$3/o;
    $state->{logtail} = $tail;

    $data->{JSON} = $state;

    return jsonresp($req, $data);
}

sub handle_zerro_respond {
    my ($req, $data) = @_;

    my $rfc1123_date = MordaX::Output::rfc1123_date($req->{'time'} || time);
    my $h = HTTP::Headers->new(
        'Status'         => 200,
        'Last_Modified'  => $rfc1123_date,
        'Content_Length' => 0,
        'Cache_Control'  => 'no-cache,no-store,max-age=0,must-revalidate',
        'Expires'        => $rfc1123_date,
        'P3P'            => 'policyref="/w3c/p3p.xml", CP="NON DSP ADM DEV PSD IVDo OUR IND STP PHY PRE NAV UNI"',
    );
    *STDOUT->syswrite($h->as_string("\015\012"));
    *STDOUT->syswrite("\015\012");

    return 1;
}

sub handle_pixel_respond {
    my ($req, $data) = @_;
    $data = "74946483931610001000080000000000000000129f401000000000c20000000010001000002020441000b3";
    my $gif = pack("h*", $data);

    return MordaX::Output::respond($req, $gif, undef, 'image/gif');
}

sub _get_weather_info {
    my ($req, $geoid) = @_;

    return undef unless ($geoid);

    my $it = {
        'geo'     => $geoid,
        'when'    => undef,
        'ewhen'   => undef,
        'alerts'  => [],
        'ealerts' => [],
    };
    $it->{'geoname'} = $MordaX::TestHelper::WeatherData{'w'}{$geoid}{'name'};

    my $prog = MordaX::Cache->get('weatherw_v2_' . $geoid);
    unless (is_hash($prog)) {
        return undef;
    }

    if (
        is_hash($prog)
        && is_hash($prog->{'brief'})
        && is_hash($prog->{'brief'}{'factual'})
        && is_hash($prog->{'brief'}{'forecast'})
        && is_hash($prog->{'brief'}{'factual'}{'condition'})
        && $prog->{'brief'}{'factual'}{'condition'}{'code'}
        && is_hash($prog->{'brief'}{'factual'}{'temperature'})

      )
    {

        $it->{'temp'}     = $prog->{'brief'}{'factual'}{'temperature'}{'content'};
        $it->{'state'}    = $prog->{'brief'}{'factual'}{'condition'}{'code'};
        $it->{'staterus'} = $MordaX::TestHelper::WeatherData{'t'}{$it->{'state'}};

        if (is_hash($prog->{'brief'}{'morda_alert'}) && is_array_size($prog->{'brief'}{'morda_alert'}{'codes'})) {
            for (@{$prog->{'brief'}{'morda_alert'}{'codes'}}) {
                push @{$it->{'alerts'}}, {
                    'code'  => $_,
                    'title' => MordaX::Lang::lang('weather.codes.' . $_),
                };
                $it->{'when'} = MordaX::Lang::lang('weather.' . $prog->{'brief'}{'morda_alert'}{'when'});
            }
        }
        my $eveningkey = 'evening_alert_' . $req->{'LocalYYYYMMDD'};
        if (is_hash($prog->{'brief'}{$eveningkey}) && is_array_size($prog->{'brief'}{$eveningkey}{'codes'})) {
            for (@{$prog->{'brief'}{$eveningkey}{'codes'}}) {
                push @{$it->{'ealerts'}}, {
                    'code'  => $_,
                    'title' => MordaX::Lang::lang('weather.codes.' . $_),
                };
                $it->{'ewhen'} = MordaX::Lang::lang('weather.' . $prog->{'brief'}{$eveningkey}{'when'}) || 'undefined';
            }
        }
    } else {
        $it->{'error'} = 'no or bad weather';
    }

    return $it;
}

sub _notempty_alert {
    my ($req, $geoid) = @_;

    my $it = _get_weather_info($req, $geoid);
    if (is_hash($it) && is_array($it->{'alerts'}) && scalar(@{$it->{'alerts'}})) {
        return 1;
    } else {
        return 0;
    }
}

sub _notempty_ealert {
    my ($req, $geoid) = @_;

    my $it = _get_weather_info($req, $geoid);
    if (is_hash($it) && is_array($it->{'ealerts'}) && scalar(@{$it->{'ealerts'}})) {
        return 1;
    } else {
        return 0;
    }
}

sub handle_weather_report {
    my ($req, $data) = @_;

    $data->{'Page'}{'Weather'} = [];
    my $wd   = $data->{'Page'}{'Weather'};
    my $page = 0;
    if (defined($req->{'Getargshash'}{'p'}) && ($req->{'Getargshash'}{'p'} =~ /^\d+$/o)) {
        $page = $req->{'Getargshash'}{'p'};
    }
    my $alertsonly  = 0;
    my $eveningonly = 0;
    if (true($req->{'Getargshash'}{'al'})) {
        $alertsonly = 1;
    } elsif (true($req->{'Getargshash'}{'ev'})) {
        $eveningonly = 1;
    }

    update_weather_index();

    my $pagesize = 100;

    my @WData = @{$MordaX::TestHelper::WeatherData{'sorted'}};

    if ($alertsonly) {
        @WData = grep { _notempty_alert($req, $_) } @WData;
    } elsif ($eveningonly) {
        @WData = grep { _notempty_ealert($req, $_) } @WData;
    }

    my $totalreports = ($alertsonly || $eveningonly) ? scalar(@WData) : $MordaX::TestHelper::WeatherData{'N'};
    my $totalpages = int(($totalreports / $pagesize) + 0.999);    # округление вверх

    $page = $totalpages - 1 if ($page > ($totalpages - 1));

    my $i0 = $page * $pagesize;
    my $i1 = $i0 + $pagesize - 1;
    $i1 = $totalreports - 1 if ($i1 > ($totalreports - 1));

    for (my $i = $i0; $i <= $i1; $i++) {
        my $curgeo = $WData[$i];

        my $it = _get_weather_info($req, $curgeo);
        next unless (defined($it));

        my $besthost = _getbesthost($curgeo);

        $it->{'geosethref'} = sprintf('http://%s/?geobyip=%s', $besthost, $curgeo);

        push @$wd, $it;
    }

    for (my $pg = 0; $pg < $totalpages; $pg++) {
        my $left  = $pg * $pagesize;
        my $right = $left + $pagesize - 1;
        $right = ($totalreports - 1) if ($right > ($totalreports - 1));
        my $item = {
            'title' => sprintf('%d..%d', $left, $right),
            'titleshort' => $pg,
            'ltitle'     => sprintf('%s-%s',
                substr($MordaX::TestHelper::WeatherData{'w'}{$WData[$left]}{'name'},  0, 3),
                substr($MordaX::TestHelper::WeatherData{'w'}{$WData[$right]}{'name'}, 0, 3)),
        };
        unless ($pg == $page) {
            $item->{'href'} = '/test/weather/';
            my $getargs = join('&', grep {$_} $pg ? "p=$pg" : 0, $alertsonly ? "al=yes" : 0, $eveningonly ? 'ev=yes' : 0);
            $item->{'href'} .= '?' . $getargs if ($getargs);
        }

        push @{$data->{'Page'}{'Weatherpages'}}, $item;
    }

    $data->{'Page'}{'currentgeo'}       = $req->{'GeoByDomainIp'};
    $data->{'Page'}{'globlalmordalink'} = sprintf('http://%s/', _getbesthost($req->{'GeoByDomainIp'}));
    $data->{'Page'}{'currentgeoname'}   = Geo::Lang::lang_geo($req->{'GeoByDomainIp'}, 'ru', 'locative');

    if ($alertsonly) {
        $data->{'Page'}{'toalldata'} = '/test/weather/';
        $data->{'Page'}{'toevening'} = '/test/weather/?ev=yes';
        $data->{'Page'}{'toalerts'}  = undef;
    } elsif ($eveningonly) {
        $data->{'Page'}{'toalldata'} = '/test/weather/';
        $data->{'Page'}{'toevening'} = undef;
        $data->{'Page'}{'toalerts'}  = '/test/weather/?al=yes';
    } else {
        $data->{'Page'}{'toalldata'} = undef;
        $data->{'Page'}{'toevening'} = '/test/weather/?ev=yes';
        $data->{'Page'}{'toalerts'}  = '/test/weather/?al=yes';
    }

    $data->{'Page'}{'ooops'} = 1 unless (scalar(@WData));

    return resp($req, 'test_weather_report.html', $data);
}

sub update_weather_index {
    my $now = time();
    if ($now - $MordaX::TestHelper::WeatherData{'ts'} < 600) {
        return;
    }

    my $mconf      = MordaX::Conf->new();
    my $exportsdir = $mconf->GetVal('ExportsDir');
    unless (-d $exportsdir) {
        logit('interr', sprintf("Directory %s configured as ExportsDir not found, failed to process /test/weather/", $exportsdir));
        return;
    }

    my $weathert0 = [Time::HiRes::gettimeofday];
    my $dh;
    my $rc = opendir($dh, $exportsdir);
    unless ($rc) {
        logit('interr', sprintf("Failed to open directory %s: %s, so failed to process /test/weather/", $exportsdir, $!));
        return;
    }

    my @files = grep {/^weather\d+\.json$/} readdir($dh);
    closedir($dh);

    for (@files) {
        my $filename = File::Spec->catfile($exportsdir, $_);
        my $fh;
        my $rc = open($fh, '<', $filename);
        unless ($rc) {
            logit('interr', sprintf("Failed to open file %s for reading: %s, some of weather data will be lost", $filename, $!));
            next;
        }
        my $fdata = join('', (<$fh>));
        close $fh;
        my $wfiledata;
        eval { $wfiledata = JSON::XS::decode_json($fdata); };
        if ($@) {
            logit('interr', sprintf("Failed to get data from file %s: %s, some of weather data will be lost", $filename, $@));
            next;
        }
        unless (is_hash($wfiledata) && is_hash($wfiledata->{'w'}) && is_hash($wfiledata->{'t'})) {
            logit('interr', sprintf("Bad data loaded from file %s: no w or t hash, some of weather data will be lost", $filename));
            next;
        }

        for my $geo (keys(%{$wfiledata->{'w'}})) {
            my $wd = $wfiledata->{'w'}{$geo};
            $MordaX::TestHelper::WeatherData{'w'}{$geo} = {'name' => $wd->{'name'},};
        }
        for my $alert (keys(%{$wfiledata->{'t'}})) {
            my $wd = $wfiledata->{'t'}{$alert};
            $MordaX::TestHelper::WeatherData{'t'}{$alert} = $wd->{'ru'};
        }
    }
    $MordaX::TestHelper::WeatherData{'ts'} = $now;
    @{$MordaX::TestHelper::WeatherData{'sorted'}} =
      sort { ($MordaX::TestHelper::WeatherData{'w'}{$a}{'name'} // '') cmp($MordaX::TestHelper::WeatherData{'w'}{$b}{'name'} // '') }
      keys(%{$MordaX::TestHelper::WeatherData{'w'}});
    $MordaX::TestHelper::WeatherData{'N'} = scalar(@{$MordaX::TestHelper::WeatherData{'sorted'}});

    my $weathert1 = Time::HiRes::tv_interval($weathert0);
    logit('debug', sprintf("Weather index loaded in %0.6f seconds. Loaded %s regions", $weathert1, $MordaX::TestHelper::WeatherData{'N'}));
#    print STDERR Data::Dumper->Dump([$MordaX::TestHelper::WeatherData{'t'}], ['T']) . "\n";
}

sub _getbesthost {
    my ($geo) = @_;

    $geo //= '213';

    my @parents = Geo::geo($geo, 'parents');
    my $country = '';
    for (@parents) {
        my $_country = $Geo::Domain::GreatCountries{$_};
        if ($_country && $MordaX::TestHelper::BestTld{$_country}) {
            $country = $_country;
            last;
        }
    }
    return sprintf('www%s.yandex.%s', $MordaX::Config::FullInstanceModifier, ($MordaX::TestHelper::BestTld{$country}));
}

%MordaX::TestHelper::WeatherData = (
    'ts' => 0,
    'w'  => {},
    't'  => {},
);

%MordaX::TestHelper::BestTld = (
    'Turkey'     => 'com.tr',
    'Belarus'    => 'by',
    'Ukraine'    => 'ua',
    'Kazakhstan' => 'kz',
    'Russia'     => 'ru',
    ''           => 'ru',
);

use Rapid::HandlerConfig;

sub handle_Rapid_config {

    my ($req, $data, $post) = @_;

    my $vars = Rapid::HandlerConfig::get_base_vars();

    my $memd     = MordaX::Cache->new();
    my $instance = MordaX::Conf->get('InstanceModifier');

    if ($post->{config}) {
        my $json = URI::Escape::XS::uri_unescape($post->{config});
        my $data = MP::Utils::parse_json($json);
        if ($data) {
            $memd->set('Rapid_config' . $instance, $data);
        }
        MordaX::Output::r200json($req, {ok => 1},);
    }

    my $get = $req->{Getargshash};
    dmp($get);
    $data->{Page}->{config} = JSON::XS->new->pretty()->utf8->encode(Rapid::HandlerConfig::get_config_json());

    return resp($req, 'test_instant_config.html', $data);
}

sub post_Rapid_config {
    my ($r, $req, $pagedata) = @_;
    my $body = $r->post_rawbody();
    my $json = URI::Escape::XS::uri_unescape($body);
    my $data = MP::Utils::parse_json($json);
    if ($data && MordaX::Utils::is_hash($data)) {

        my $memd     = MordaX::Cache->new();
        my $instance = MordaX::Conf->get('InstanceModifier');
        $memd->set('Rapid_config' . $instance,         $data);
        $memd->set('Rapid_config' . $instance . "_ts", time);
    } else {
        return MordaX::Output::r200json(
            $req, {
                ok    => 0,
                error => $@
            },
        );
    }
    MordaX::Output::r200json($req, {ok => 1},);

}

sub handle_dumpvars {
    my ($req, $data, $post) = @_;
    $data->{Page}->{exports} = [keys %MordaX::Data::storage];
    return resp($req, 'test_dumpvars.html', $data);
}

sub handle_yabs_stripe {
    my ($req, $data, $post) = @_;
    #$data->{Page}->{exports} = [ keys %MordaX::Data::storage ];
    return resp($req, 'test_yabs.html', $data);
}

sub handle_display {
    my ($req, $data, $postargs) = @_;

    my $p = $data->{'Page'};

    $p->{'szm'} = $req->{'YCookies'}->value('szm');
    $p->{'sz'} = $req->{'YCookies'}->value('sz');

    return resp($req, 'test/test_display.html', $data);
}

sub handle_tv {
    my ($req, $data, $post) = @_;
    #$data->{Page}->{exports} = [ keys %MordaX::Data::storage ];
    return resp($req, 'test/tv.html', $data);
}

sub handle_yb_cookie {
    my ($req, $data) = @_;

    my $page = $data->{'Page'};

    if ($req->{'Getargshash'}) {
        $page->{'type'} = $req->{'Getargshash'}->{'type'};
    }

    return resp($req, 'test_ybcookie.html', $data);
}

sub post_log_csp {

    my ($r, $req, $data) = @_;
    my $post   = $r->post_rawbody();
    my $showid = $req->{Getargshash}->{showid};
    if ($showid) {
        $req->{'Requestid'} = $MP::Logit::Requestid = $showid;
    }
    if ($post) {
        my $json = MP::Utils::parse_json($post, 0);
        if ($json and $json->{'csp-report'}) {
            my $d = $json->{'csp-report'};
            logit('warning', "##cn#CSP##wn# BLOCKED: ##rn#" . $d->{"blocked-uri"});
            logit('warning', "##cn#CSP##wn# VIA:    " . $d->{"violated-directive"});
            logit('warning', "##cn#CSP##wn# FROM:   " . $d->{"document-uri"});
        }
    }

    MordaX::Output::r200json($req, {ok => 1},);
}

sub handle_kote_post {
    my ($r, $req, $data) = @_;
    my $post   = $r->post_rawbody();
    return MordaX::Output::r200json($req, {ok => "Error: Empty request body"}) unless $post;
    my $encoded_text_from_test_field;
    my $encoded_text_from_mock_field;
    my $json;
    my $timestamp;

    eval{$json = MP::Utils::parse_json($post)};
    return MordaX::Output::r200json($req, {ok => "$@"}) unless $@ eq "";

    if ($json->{get_file}){
        my $file_path = $json->{get_file};
        open(FH, '<:utf8', "../function_tests/tests/kote/tests/$file_path") or return MordaX::Output::r200json($req, {yaml => "Unable to open ../function_tests/tests/kote/tests/$file_path"},);
        my $text_from_test_file = do { local $/ = <FH> };
        return MordaX::Output::r200json($req, {ok => '1', yaml => $text_from_test_file},);
    }
    my ($sec, $min, $hour, $mday, $mon, $year) = localtime(time);
    my ($seconds, $microseconds) = Time::HiRes::gettimeofday;
    $timestamp = sprintf('_%02d.%02d.%d_%02d:%02d:%02d.%06d', $mday, $mon + 1, $year + 1900, $hour, $min, $sec, $microseconds);
    $encoded_text_from_test_field = $json->{test_input};
    return MordaX::Output::r200json($req, {ok => "Error: Empty test field"}) if $encoded_text_from_test_field eq "";
    if ($json->{mock}) {
        $encoded_text_from_mock_field = $json->{mock};
    }

    my @splited_input = split('result:', $encoded_text_from_test_field);
    #докидываем клиент и путь для проверки моков при необходимости
    if ($splited_input[0] !~ /config:/) {
        $encoded_text_from_test_field = "config:\n  client: mock\n  path: /tmp/mock_file$timestamp.json\n".$encoded_text_from_test_field;
    } elsif ($splited_input[0] =~ /client:\s+mock/ && $splited_input[0] !~ /path/) {
        $encoded_text_from_test_field =~ s!config:!config:\n  path: /tmp/mock_file$timestamp.json!;
    }
    #докидываем блок meta при необходимости
    @splited_input = split('result:', $encoded_text_from_test_field);
    if ($splited_input[0] !~ /meta:/) {
        $encoded_text_from_test_field = "meta:\n  task: HOME-0\n  desc: ''\n".$encoded_text_from_test_field;
    }
    if ($splited_input[0] !~ /task:/ && $splited_input[0] =~ /meta:/) {
        $encoded_text_from_test_field =~ s/meta:\n/meta:\n  task: HOME-0\n/;
    }
    if ($splited_input[0] !~ /desc:/ && $splited_input[0] =~ /meta:/) {
        $encoded_text_from_test_field =~ s/meta:\n/meta:\n  desc: ''\n/;
    }

    my $morda_env = $json->{morda_env};
    if (not(-e '../function_tests/venv/')) {
        system("cd ../function_tests; make init");
    }

    open(FH,'>:utf8',"/tmp/test_file$timestamp.yaml") or return MordaX::Output::r200json($req, {ok => "Unable to open /tmp/test_file$timestamp.yaml"},);
    print FH $encoded_text_from_test_field;
    close(FH) or return MordaX::Output::r200json($req, {ok => "Unable to close /tmp/test_file$timestamp.yaml"},);
    if (defined($encoded_text_from_mock_field)) {
        open(FH,'>:utf8',"../function_tests/tests/kote/tests/framework_test/mocks/tmp/mock_file$timestamp.json") or return MordaX::Output::r200json($req, {ok => "Unable to open ../function_tests/tests/kote/tests/framework_test/mocks/tmp/mock_file$timestamp.json"},);
        print FH $encoded_text_from_mock_field;
        close(FH) or return MordaX::Output::r200json($req, {ok => "Unable to close ../function_tests/tests/kote/tests/framework_test/mocks/tmp/mock_file$timestamp.json"},);
    }
    system("cd ../function_tests/; ./venv/bin/py.test tests/kote/test_run_tests.py -s --tests_path=/tmp/test_file$timestamp.yaml --morda_env=$morda_env >> /tmp/test_output$timestamp");
    system("rm /tmp/test_file$timestamp.yaml");
    if (-e "../function_tests/tests/kote/tests/framework_test/mocks/tmp/mock_file$timestamp.json") {
        system("rm ../function_tests/tests/kote/tests/framework_test/mocks/tmp/mock_file$timestamp.json");
    }
    open(FH,'<:utf8',"/tmp/test_output$timestamp") or return MordaX::Output::r200json($req, {ok => "Unable to open /tmp/test_output$timestamp"},);
    my $text_from_file = do { local $/ = <FH> };
    close(FH) or return MordaX::Output::r200json($req, {ok => "Unable to close /tmp/test_output$timestamp"},);
    system("rm /tmp/test_output$timestamp");

    return MordaX::Output::r200json($req, {ok => $text_from_file},);
}

sub handle_node_dev_tools {
    my ($req, $data) = @_;

    my $host = MP::Utils::hostname();
    my $origin = $host . ':' . MordaX::Conf->get('FrontNodeInspectPort');
    my $url = 'http://' . $origin . '/json/list';
    my $http_agent = MordaX::HTTP->new($req);
    $http_agent->add(
        'alias'   => 'node_devtools',
        'url'     => $url,
        'timeout' => 2,
        'retries' => 0,
        'can_v6'  => 1,
        'slow'    => 1,
        'headers' => [
            # https://github.com/Microsoft/vscode/issues/48392#issuecomment-383981252
            { name => 'Host', value => 'localhost' }
        ]
    );
    my $res = $http_agent->result_req_info('node_devtools')->{response_content};
    my $json = JSON::XS::decode_json($res);
    my $devtools = $json->[0]->{'devtoolsFrontendUrl'};
    my $ip = DNS::get_ip_by_name($host);
    my $port = MordaX::Conf->get('FrontNodeInspectPort');
    my $devtools2;

    $devtools =~ s/localhost\//[$ip]:$port\//;
    $devtools2 = $devtools;
    $devtools2 =~ s/chrome-devtools:\/\//devtools:\/\//;

    my $p = $data->{'Page'};
    $p->{'devtools'} = $devtools;
    $p->{'devtools2'} = $devtools2;
    $p->{'ip'} = $ip;
    $p->{'port'} = $port;
    $p->{'host'} = $host;

    resp($req, 'test_devtools.html', $data);

    eval { MordaX::HTTP::Handler->clean();};
}

sub handle_antiaddblock {
    my ($req, $data) = @_;

    resp($req, 'test/antiaddblock.html', $data);
}

sub handle_themes {
    my ($req, $data) = @_;

    my $p = $data->{'Page'};
    $p->{sk} = $req->{sk};

    resp($req, 'test/themes.html', $data);
}

sub handle_kote {
    my ($req, $data) = @_;
    my $dir = '../function_tests/tests/kote/tests';
    my $files = `find $dir`;
    my @files = split(/\n/, $files);
    my @files_for_list;
    foreach my $file_name(@files){
        if ($file_name =~ /.yaml/ && !($file_name =~ /\/framework_test\//) && $file_name =~ /test_/){
            $file_name =~ s/$dir\///;
            push(@files_for_list, $file_name);
        }
    }
    my $json_list = encode_json(\@files_for_list);
    my $p = $data->{Page};
    $p->{FILE_LIST} = $json_list;
    $p->{HOST} = $req->{HostName};
    #обрезаю HOST, чтобы не было ошибки при запуске тесов на деве
    $p->{HOST} =~ s/.yandex.ru//;
    resp($req, 'test/kote.html', $data);
}

sub handle_dzensearch_desktop {
    my ($req, $data) = @_;

    resp($req, 'test/dzensearchdesktop.html', $data);
}

sub handle_dzensearch_touch {
    my ($req, $data) = @_;

    resp($req, 'test/dzensearchtouch.html', $data);
}

1;
