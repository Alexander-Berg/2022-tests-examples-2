package Test::UserInfo;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);
use MordaX::HTTP;

use MordaX::Logit qw(dmp logit);
use MordaX::Utils;
use MordaX::Auth;

use MP::Utils;
use MordaX::Data_load;
use MordaX::Data_get;
use MP::DTS;
use Geo::Lang;
use TestHelper qw(no_register);

sub handler {
    my ($req, $data) = @_;

    $req->{'_STATBOX_ID_SUFFIX_'} = 'test'; # HOME-37938
    MordaX::Auth::auth($req);
    $req->{AuthInfo} = $req->{AuthOBJ}{INFO};

    my $login = $req->{Getargshash}->{login} || $req->{AuthInfo}->{login};
    my $yaid  = $req->{Getargshash}->{yaid}  || $req->{yandexuid};
    my $userinfo = $req->{AuthOBJ}->UserInfo($req, {login => $login, emails => 'getall'},);
    my $uid = $userinfo->{uid};
    $data->{Page}{login}     = $login;
    $data->{Page}{yaid}      = $yaid;
    $data->{Page}{req_login} = $req->{AuthInfo}->{login};
    $data->{Page}{req_yaid}  = $req->{yandexuid};

    suggest($req, $data, $login);
    yandex_services($req, $data, $yaid);

    apps($req, $data, "yaid-$yaid");
#    apps($req, $data, $uid);

    cine($req, $data, $uid);

    return TestHelper::resp($req, 'test/userinfo.html', $data);
}

my %applist = (
    554 => "Yandex.Disk",
    550 => "Яндекс.Браузер iOS Tablet",
    582 => "Yandex.Search for WP",
    572 => "Yandex.Trains Android",
    547 => "Яндекс.Браузер Android Phone",
    557 => "Yandex.Maps Android",
    564 => "Яндекс.Музыка WP",
    579 => "library Account Manager (Production)",
    577 => "УгадайКино! (Production)",
    571 => "Yandex.Weather",
    566 => "Yandex.News",
    561 => "Yandex.Master iOS",
    559 => "Yandex.Market IOS",
    553 => "Yandex.Direct",
    581 => "Яндекс.Медали (Production)",
    573 => "Yandex.Trains IOS",
    576 => "Yandex.Translate for iOS",
    555 => "Yandex.Mail Android",
    583 => "Yandex.Store",
    552 => "Яндекс.Город iOS",
    578 => "КиноПоиск (Production)",
    548 => "Браузер Android Tablet",
    575 => "Yandex.Translate for WP",
    565 => "Яндекс.Музыка iOS",
    569 => "Yandex.Shell",
    584 => "Yandex.Metro (Production)",
    563 => "Яндекс.Музыка Android",
    551 => "Яндекс.Город Android",
    570 => "Яндекс.Транспорт (Production)",
    580 => "Яндекс.ЕГЭ (прод)",
    562 => "Яндекс.Музыка (NEW)",
    567 => "Yandex.News Android",
    546 => "Афиша (Android)",
    560 => "Yandex.Market WP",
    574 => "Yandex.Translate for Android",
    556 => "Yandex.Maps (Production)",
    549 => "Яндекс.Браузер iOS Phone",
    585 => "Yandex.Taxi (Production)",
    558 => "Yandex.Market Android",
    568 => "Yandex.Parking(Production)",
);

sub apps {
    my ($req, $data, $id) = @_;

    $data->{Page}{Apps} = [];
    # make bigb request HOME-36600
}

sub cine {
    my ($req, $data, $uid) = @_;

    my $rid     = MP::DTS::init_yatickets($req, $uid);
    my $batch_request_id = MP::DTS::run_request($req, $uid);
    my $tickets = MP::DTS::personal_storage_response($req, $rid);

    foreach my $ticket (@{$tickets->{items}}) {
        $ticket->{session}{venue}{region_name} = Geo::Lang::lang_geo($ticket->{session}{venue}{region_id}, $req->{'Locale'});
    }
    $data->{Page}{Cine} = $tickets->{items} || [];
}

sub suggest {
    my ($req, $data, $login) = @_;

    my $url  = "http://suggest-internal.yandex.ru/suggest-ub?yandex_login=$login";
    my $http = MordaX::HTTP->new($req);
    $http->add(
        'alias'   => 'userinfo_suggest',
        'url'     => $url,
        'timeout' => 0.2,
        'retries' => 1,
    );

    my $reply = $http->result_req_info('userinfo_suggest');

    if ($reply->{error}) {
        return undef;
    }
    my $suggest = MP::Utils::parse_json($reply->{response_content});
    return unless (MordaX::Utils::is_hash_size($suggest));

    $data->{Page}{Suggest}{has_auto} = $suggest->{has_auto} || 'no';

    my $geos_interest = [];
    my $geos_tourist  = [];
    foreach my $key (keys(%$suggest)) {
        if ($key =~ m/^\d+$/o) {
            push @$geos_interest, {
                id    => $key,
                name  => Geo::Lang::lang_geo($key, $req->{'Locale'}),
                value => $suggest->{$key}
            };
        }
        if ($key =~ m/^\d+t$/o) {
            my $geoid = substr($key, 0, -1);
            push @$geos_tourist, {
                id    => $geoid,
                name  => Geo::Lang::lang_geo($geoid, $req->{'Locale'}),
                value => $suggest->{$key}
            };
        }
    }
    $data->{Page}{Suggest}{geos_interest} = $geos_interest;
    $data->{Page}{Suggest}{geos_tourist}  = $geos_tourist;
}

sub yandex_services {
    my ($req, $data, $yaid) = @_;
    MordaX::Data_load::init_datas();

    my @headers = (
        {
            'name'  => 'Cookie',
            'value' => 'yandexuid=' . $yaid,
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
    my $yabs_data = MP::Utils::parse_json($yabs_json);

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

    $data->{Page}{Services} = [sort { $b->{weight_adjusted} <=> $a->{weight_adjusted} } @sites];

    my @external_sites;
    my %external_id2site;
    foreach my $record (@{MordaX::Data_get::get_static_data($req, 'services_external', all => 1)}) {
        foreach my $id (split /,/, $record->{id}) {
            $external_id2site{$id} = {%$record};
            $external_id2site{$id}->{id} = $id;
        }
    }
    foreach my $record (grep { $_->{id} == 198 } @{$yabs_data->{data}->[0]->{segment}}) {
        foreach my $id (split(/,/, $record->{value})) {
            next unless ($external_id2site{$id});
            push @external_sites, {id => $id, name => $external_id2site{$id}->{url}};
        }
    }

    $data->{Page}{ExternalSites} = \@external_sites;

    #return resp($req, 'testsites.html', $data)

}

1;
