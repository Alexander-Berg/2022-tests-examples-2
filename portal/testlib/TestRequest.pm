package testlib::TestRequest;

use strict;
use warnings;
use utf8;
use v5.14;
use mro 'c3';

package testlib::TestRequest::FcgiRequest;
use rules;

use base q(MordaX::FcgiRequest);
use rules;

use MP::Logit;
use MP::Utils;

use MordaX::Utils;

use URI::Escape::XS;
use URI::Split;

sub new {
    my ($class, %args) = (shift, @_);

    local %ENV = ();

    $ENV{'X-Real-IP'} = $args{'ip'} || '213.180.217.26';    #some yandex ip

    if (is_hash_size(my $cookies = $args{'cookies'})) {
        $ENV{'HTTP_COOKIE'} = join '; ', map {
            URI::Escape::XS::uri_escape($_)
              . '='
              . URI::Escape::XS::uri_escape($cookies->{$_})
        } keys %$cookies;
    }

    if (is_hash_size(my $headers = $args{'headers'})) {
        for my $key (keys %$headers) {
            my $name = uc "HTTP-$key";
            $name =~ tr/-/_/;
            $ENV{$name} = $headers->{$key};
        }
    }

    my ($scheme, $host, $path, $query) =
      ('https', $args{'host'} || 'www.yandex.ru', '/', '');

    if (my $url = $args{'url'}) {
        my ($_scheme, $_host, $_path, $_query) = URI::Split::uri_split($url);
        if (defined $_host) {
            $scheme = $_scheme if $_scheme;
            $host   = $_host   if $host;
            $path   = $_path   if length $_path;
            $query  = $_query  if defined $_query;
        }
    }

    if (is_array(my $_path = $args{'path'})) {
        $path = '/' . join '/', @$_path;

    }

    if (is_hash_size(my $_query = $args{'query'})) {
        $query = MordaX::Utils::make_args_string(%$_query);
    }

    $ENV{'SCHEME'}      = $scheme;
    $ENV{'HTTP_HOST'}   = lc $host;
    $ENV{'REQUEST_URI'} = $path;
    $ENV{'REQUEST_URI'} .= '?' . $query if length $query;

    $ENV{'NGINX_INTERFACE'} = $args{'interface'} || 'bigmorda';

    $ENV{'HTTP_CONTENT_LENGTH'} = 0;

    if (is_hash_size(my $post = $args{'post'})) {
        my $data = MordaX::Utils::make_args_string(%$post);
        { use bytes; $ENV{'HTTP_CONTENT_LENGTH'} = length $data; }
        $ENV{'HTTP_CONTENT_TYPE'} = 'application/x-www-form-urlencoded';
        $ENV{'REQUEST_METHOD'}    = 'POST';
        $ENV{'REQUEST_BODY_TEST'} = $data;
    }

    if (my $time = $args{'time'}) {
        no warnings 'redefine';
        local *Time::HiRes::time = sub {$time};
        return $class->next::method();
    }
    else {
        return $class->next::method();
    }
}

package testlib::TestRequest::Req;

use testlib::HTTP;
use MordaX::Input;

use base qw(MordaX::Req);

sub new {
    my ($class, %args) = (shift, @_);
    my $r = $args{'r'} // testlib::TestRequest::FcgiRequest->new(@_);
    my $req = $class->next::method(r => $r);
    $req->{ __PACKAGE__ . '::FcgiRequest' } = $r;
    $req->{'_HTTP_'} = testlib::HTTP->new();
    $req->{'autotests_staff_login'} = 1 if $args{test_669};
    $req->test_input(@_) unless $args{'no_input'};
    $req->{TargetingInfoComplete} //= 1;
    return $req;
}

sub test_input {
    my $req = shift;
    my $r   = $req->{'cgireq'};
    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub { MordaX::Experiment::AB::Flags::instance($_[0], 'MUTE_WARNINGS'); };
    local *MP::Tvm::get_tickets_start_request = sub { }
      if MP::Utils::get_pkg_sub('MP::Tvm', 'get_tickets_start_request');
    MordaX::Input->new(r => $r, req => $req);
    return 1;
}

sub test_http { $_[0]->{'_HTTP_'} }

sub test_setexp {
    my $req = shift;
    @{$req->{exp}->{$_}}{qw(on id)} = (1, $_) for @_;
    return $req;
}

package testlib::TestRequest::Req::Big;

use base qw(testlib::TestRequest::Req);

sub new {
    my ($class, %args) = (shift, @_);
    my $headers = $args{'headers'} //= {};
    # Some Big UA
    $headers->{'User-Agent'} =
      'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0';
    return $class->next::method(%args);
}

package testlib::TestRequest::Req::Touch;

use base qw(testlib::TestRequest::Req);

sub new {
    my ($class, %args) = (shift, @_);
    my $headers = $args{'headers'} //= {};
    # Some Touch UA
    $headers->{'User-Agent'} =
      'Mozilla/5.0 (Linux; Android 8.0.0; G8232 Build/41.3.A.2.58) '
      . 'AppleWebKit/537.36 (KHTML, like Gecko) '
      . 'Chrome/64.0.3282.137 Mobile Safari/537.36';
    return $class->next::method(%args);
}

package testlib::TestRequest::Req::ApiSearch2;

use base qw(testlib::TestRequest::Req);

sub new {
    ## no critic (Home::AppVersionStrict)
    my ($class, %args) = (shift, @_);
    my $headers          = $args{'headers'} //= {};
    my $os_version       = delete($args{os_version}) // '99';
    my $app_version      = delete($args{app_version}) // '9999999';
    my $app_platform     = delete($args{app_platform}) // 'android';
    my $app_version_name = delete($args{app_version_name}) // '99.99';
    # API search ua
    $headers->{'User-Agent'} =
      "Mozilla/5.0 (Linux; Android $os_version; XXX Build/XXX; wv) "
      . "AppleWebKit/537.36 (KHTML, like Gecko) "
      . "Version/4.0 Chrome/70.0.3538.80 Mobile Safari/537.36 "
      . "YandexSearch/$app_version_name";
    $args{'path'} //= [qw(portal api search 2)];
    my $query = $args{'query'} //= {};
    $query->{app_version}      = $app_version;
    $query->{app_platform}     = $app_platform;
    $query->{os_version}       = $os_version;
    $query->{app_version_name} = $app_version_name;
    return $class->next::method(%args);
    ## use critic
}

sub test_input {
    my $req = shift;
    $req->{api_name}         = "search";
    $req->{api_search}       = 2;
    $req->{api_version}      = 2;
    $req->{real_api_name}    = 'search';
    $req->{real_api_version} = 2;
    return $req->next::method(@_);
}

1;
