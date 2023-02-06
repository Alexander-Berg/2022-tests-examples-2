package Test::ErrorLog;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);
use JSON::XS;

use MP::Logit;
use MordaX::Output;
use MordaX::Config;

use Rapid::Base;
use Rapid::Req;

sub handle {
    my ($r, $req) = @_;
    ## no critic (Variables::RequireInitializationForLocalVars)
    local $MordaX::Logit::setuplogging;
    ## use critic
    MordaX::Logit::setup(0);

    $req = Rapid::Req->new(req => $req);
    Rapid::Base::run_require_for('handler', 'errorlog', [qw/input init component block/], $r, $req,);
    my $output = Rapid::Base::get_handler('errorlog', $r, $req,);
    #dmp( $output );

    my $headers = {};

    my $origin = $r->header('Origin');
    if ($origin) {
        $headers->{'Access-Control-Allow-Origin'} = $origin;
    }

    return MordaX::Output::respond($req, $output, [], 'text/javascript', $headers);
}

Rapid::Base::handler 'errorlog',
    require => {
        input => [qw/getargs/],
    },
    call => sub {
        my ($r, $req, $args) = @_;
        my $get = $req->{'Getargshash'};
        my @data;
        my $reqid = $get->{'Requestid'};
        # FIXME FIXME FIXME: не должно быть никаких qx `` system и т.д.!!!!
        # это потенциальный RCE
        # файлы надо читать самим перлом !!!!
        if ($reqid =~ /^[-0-9a-z.]+$/i && -f $r->{context}{log}) {
            # Хоть у нас и строгая регшулярка но так как используется qx то
            # эскейпим потенциальные shell уязвимости
            $reqid =~ s,','"'"',g; #' mc
            my $command = qq{fgrep -a '[$reqid]' $r->{context}{log}};
            my $errors  = qx{$command};
            $errors =~ s/\x1B\[\d*;\d*;*\d*m//gm;    # strip colors
            for my $msg (split /[\n\r]+/, $errors) {
                if ($msg =~ s/^\s*(?<ts>\[([^\]]+)\]) (?<id>\[([^\]]+)\]) (?<uid>\[([^\]]*)\]) (?<prep>\[([^\]]+)\]) //) {
                    push @data, {%+, msg => $msg};
                }
            }

            my $node_log = MordaX::Conf->get('LogDir') . '/node.error_log.' . MP::Time::strftime_ts('%Y%m%d', $req->{'time'}, 'Europe/Moscow');
            if ($MordaX::Config::DevInstance) {
                $command = qq{fgrep -a '[$reqid]' $node_log};
            } else {
                $command = qq{fgrep -a 'reqid=$reqid' $node_log | grep 'message='};
            }
            $errors  = qx{$command};
            $errors =~ s/\x1B\[\d*;\d*;*\d*m//gm;    # strip colors
            for my $msg (split /[\n\r]+/, $errors) {
                if ($MordaX::Config::DevInstance) {
                    if ($msg =~ s/^\s*(?<ts>\[([^\]]+)\]) (?<pid>\[([^\]]+)\]) (?<prep>\[([^\]]+)\]) (?<id>\[([^\]]*)\]) //) {
                        my $vals = {%+};
                        $vals->{prep} = lc $vals->{prep};
                        $vals->{prep} =~ s/\[/[tmpl/;
                        $vals->{prep} =~ s/tmplwarn/tmplwarning/;
                        $vals->{msg} = $msg;
                        push @data, $vals;
                    }
                } else {
                    my @vals = split '\t', $msg;
                    my %hash;
                    for my $p (@vals) {
                        my ($k, $v) = split('=', $p, 2);
                        $hash{$k} = $v // '';
                    }
                    if ($hash{'timestamp'} && $hash{'level'} && $hash{'message'}) {
                        my $msg = $hash{'message'};
                        if ($hash{'stack'}) {
                            $msg .= ', stack = ' . $hash{'stack'};
                        }
                        push @data, {
                            ts => "[$hash{'timestamp'}]",
                            msg => $msg,
                            prep => "[tmpl$hash{'level'}]"
                        };
                    }
                }
            }
        } else {
            push @data, {error => 'no Requestid'};
        }

        my $output =                                 # $r->{context}{log};
            JSON::XS->new->canonical(1)->pretty(1)->allow_unknown(1)->encode(\@data);
        return $output;
    };

1;

