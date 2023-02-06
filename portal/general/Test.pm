package Handler::Test;

use lib::abs;
use rules;

use utf8;

use Plack::Builder qw(builder mount enable);
use Plack::Response;
use Plack::Request;

use HTTP::Status qw(:constants);

use Smoo::Output;

my @HANDLERS = (
    {
        name => 'add.sh',
        desc => 'port of @wwax add.sh script',
        path => '/add_sh',
        call => \&add_sh,
    },
    {
        name => 'activate.sh',
        desc => 'port of @wwax activate.sh script',
        path => '/activate_sh',
        call => \&activate_sh,
    },
    {
        name => 'error_log',
        desc => 'tail -n 500 of error.log',
        path => '/error_log',
        call => \&error_log,
    },
);

my $tt;
BEGIN {
    eval '
        require Template;
        $tt = Template->new({
            INCLUDE_PATH => lib::abs::path(q(view_test/)),
            INTERPOLATE  => 1,
        });
    ';
};

*main_ok = builder {
    for my $handler (@HANDLERS) {
        mount $handler->{'path'} => $handler->{'call'};
    }
    mount '/' => \&menu;
};

*main_fail = builder {
    enable "Plack::Middleware::ErrorDocument",
      500        => lib::abs::path('../../view_test/template_fail.html'),
      subrequest => 0,
    ;
    mount '/' => sub { Plack::Response->new(HTTP_INTERNAL_SERVER_ERROR)->finalize };
};

*main = $tt ? \&main_ok : \&main_fail;

sub menu {
    my $env = shift;
    my $req = Plack::Request->new($env);
    my $path = $req->base->path;
    my @menu;
    for my $handler (@HANDLERS) {
        my $h_path = $path . $handler->{'path'};
        $h_path =~ tr,/,/,s;
        push @menu, {
            name => $handler->{'name'},
            desc => $handler->{'desc'},
            path => $h_path,
        };
    }
    _output_template('menu.tt', { menu => \@menu });
}

sub add_sh {
    my $req = Plack::Request->new(shift);
    my $example = '{
	"name"       : "weather_tomorrow",
	"geo"        : 213,
	"locale"     : "ru",
	"msg"        : "Минюст РФ включил в реестр иноагентов девять СМИ",
	"content_id" : "random_content_id",
	"ttl_sup" : 300,
	"url" : "morda://",
}';
    my $rows = 5;
    my $cols = 0;
    for my $row (split "\n", $example) {
        $rows++;
        my $l = length($row) + 10;
        $cols = $l if $l > $cols;
    }
    _output_template('add_sh.tt', {
        example => $example,
        rows => $rows,
        cols => $cols,
        url => '/write/event/add',
    });
}

sub activate_sh {
    _output_template('activate_sh.tt', {
        url => '/write/event/activate_list',
    });
}

sub error_log {
    my $log = qx(tail -n 500 /var/log/www/portal-morda-smoothie/error.log 2>&1);
    _output_template('error_log.tt', {
            log => $log,
    });
}

sub _output_template {
    my ($name, $vars) = @_;
    my $output = '';
    unless ($tt->process($name, $vars, \$output)) {
        my $res = Plack::Response->new(HTTP_INTERNAL_SERVER_ERROR);
        $res->body($tt->error());
        return $res->finalize;
    }

    my $res = Plack::Response->new(HTTP_OK);
    $res->content_type('text/html');
    utf8::encode($output) if utf8::is_utf8($output);
    $res->body($output);
    return $res->finalize;
}

1;
