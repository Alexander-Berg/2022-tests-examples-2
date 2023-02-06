package Test::Personal;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);
use JSON::XS;
use MordaX::HTTP;

use MordaX::Logit qw(dmp logit);
use MordaX::Auth;
use Geo::Lang;

use MordaX::Block::Route;

use MP::DTS;
use MP::Time;
use TestHelper qw(no_register);

sub tickets {
    my ($req, $data, $post) = @_;
    $req->{'_STATBOX_ID_SUFFIX_'} = 'test'; # HOME-37938
    MordaX::Auth::auth($req);
    $req->{AuthInfo} = $req->{AuthOBJ}{INFO};

    if (%$post) {
        dmp $post;
    }

    my $login = $req->{Getargshash}->{login} || $req->{AuthInfo}->{login};
    my $userinfo = $req->{AuthOBJ}->UserInfo($req, {login => $login});
    my $uid = $userinfo->{uid};
    $data->{Page}{login}     = $login;
    $data->{Page}{req_login} = $req->{AuthInfo}->{login};
    $data->{Page}->{user_id} = $uid;

    my $rid          = MP::DTS::init_yatickets($req, $uid);
    my $batch_request_id = MP::DTS::run_request($req, $uid);
    my $tickets_data = MP::DTS::personal_storage_response($req, $rid);

    foreach my $ticket (@{$tickets_data->{items}}) {
        my $id_html = $ticket->{id};
        $id_html = s/[^a-zA-Z0-9\-_]/_/go;
        $ticket->{id_html} = $id_html;
        $ticket->{session}{venue}{region_name} = Geo::Lang::lang_geo($ticket->{session}{venue}{region_id}, $req->{'Locale'});
    }

    $data->{Page}{Tickets} = $tickets_data->{items} || [];

    return TestHelper::resp($req, 'test/personal/tickets.html', $data);
}

sub traffic {
    my ($req, $data, $post) = @_;

    $req->{'_STATBOX_ID_SUFFIX_'} = 'test'; # HOME-37938
    MordaX::Auth::auth($req);
    my $get  = $req->{Getargshash};
    my $auth = $req->{AuthOBJ};
    my $json = JSON::XS->new->pretty()->canonical->utf8;
    #dmp( $auth->{INFO} );
    #logit('interr', "Logging?");

    my $uid = $get->{uid} || $auth->{INFO}->{uid};
    my $page = $data->{Page} ||= {};
    $page->{uid} = $uid;

    $req->{AuthInfo} = {
        logged => 1,
        uid    => $uid,
    };
    my $widget_id = $get->{wid} || '_traffic-1';
    my $request_id = MP::DTS::init_addresses($req, $uid);;
    my $batch_request_id = MP::DTS::run_request($req, $uid);

    my $personal_storage_res = MP::DTS::personal_storage_response($req, $request_id);
    my $widget_points = MordaX::Block::Route::parse_datasync_addresses($personal_storage_res, $widget_id);

    my $raw = [
        MP::DTS::personal_storage_response($req, $request_id),
    ];
    $page->{points} = $json->encode($widget_points || {});
    $page->{raw}    = $json->encode($raw || {});
    return TestHelper::resp($req, 'test/personal/traffic.html', $data);
}

1;

