package MordaX::HTTP::Degradation::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::HTTP;
use Home::Kernel::Degradation;
use Home::Kernel::Context qw(Ctx);
use Home::Kernel::ContextPolicy;
use testlib::TestRequest;
use MordaX::Data_load;
MordaX::Data_load::init_datas();

my $ctx_policy = Home::Kernel::ContextPolicy->new({});
my $init = Ctx->init($ctx_policy);

# подменяем данные из экспорта деградации
my $degradation = {
    http_alias => {
        req1 => {
            args => {
                "*" => 1
            }
        }
    }
};
Ctx->save(Home::Kernel::Degradation::HOME_CTX_KEY, $degradation);

sub error_callback : Test(6) {
    my $req = {
        handler => "Handler::Api",
        time => time(),
    };
    my $http = MordaX::HTTP->new($req);
    isa_ok($http, "MordaX::HTTP::Degradation");
    my $alias = "req1";
    my $req_info = $http->add(
        "alias"   => $alias,
        "suffix"  => "reqtype_1",
        "url"     => "http://127.0.0.1:9999",
        "timeout" => 0.9,
        "retries" => 3,
        "progressive" => 0,
        "error_callback" => sub {
            my ($req_info, $error_callback_data, $http) = @_;
        },
        "error_callback_data" => "",
    );
    is($req_info, 1, "add - another interface");
    ok(!exists $http->{degradated_aliases}, "has not prop degradated_aliases");
    is($http->alias_exists($alias), "", "alias_exists - false");
    is($http->result_wait($alias), 1, "result_wait");

    $req_info = $http->result_req_info($alias);
    cmp_deeply($req_info, {error=>1, success=>0, alias => $alias}, "req_info");
}

sub no_error_callback : Test(6) {
    my $req = {
        handler => "Handler::Api",
        time => time(),
    };
    my $http = MordaX::HTTP->new($req);
    isa_ok($http, "MordaX::HTTP::Degradation");
    #explain($http);
    my $port = 9999;
    my $alias = "req1";
    my $req_info = $http->add(
        "alias"   => $alias,
        "suffix"  => "reqtype_1",
        "url"     => "http://127.0.0.1:$port",
        "timeout" => 0.9,
        "retries" => 3,
        "progressive" => 0,
    );
    is($req_info, 1, "add - another interface");
    cmp_deeply($http, noclass(superhashof({degradated_aliases => {$alias => 1}})), "has prop degradated_aliases");

    is($http->alias_exists($alias), "1", "alias_exists - true");
    is($http->result_wait($alias), undef, "result_wait");

    $req_info = $http->result_req_info($alias);
    cmp_deeply($req_info, {error=>1, success=>0, alias => $alias}, "req_info");
}

1;
