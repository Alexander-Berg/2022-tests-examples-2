package Test::BlockDisplay;

use rules;    #common v2
use MP::Stopdebug;

use lib::abs qw(../);
use JSON::XS;
use POSIX qw( );

use MordaX::Logit qw(dmp logit);
use MordaX::Conf;
use MordaX::Output;

use Rapid::Base (qw/handler/);
use Rapid::Req;

use Utils::Tskv;

sub handle {
    my ($r, $req) = @_;

    ## no critic (Variables::RequireInitializationForLocalVars)
    local $MordaX::Logit::setuplogging;
    ## use critic
    MordaX::Logit::setup(0);

    $req = Rapid::Req->new(req => $req);
    Rapid::Base::run_require_for('handler', 'blockdisplay', [qw/input init component block/], $r, $req,);
    my $output = Rapid::Base::get_handler('blockdisplay', $r, $req,);

    my $headers = {};

    my $origin = $r->header('Origin');
    if ($origin) {
        $headers->{'Access-Control-Allow-Origin'} = $origin;
    }

    return MordaX::Output::respond($req, $output, [], 'text/javascript', $headers);
}

handler 'blockdisplay',
    require => {
        input => [qw/getargs time/]
    },
    call => sub {
        my ($r, $req, $data) = @_;
        my $args = $req->{'Getargshash'};

        #dmp( $req );
        #dmp( $args );
        my @v1data;
        my $tskv_data = {};

        my $date = POSIX::strftime("%Y%m%d", localtime($req->{time}));

        my $Requestid = $args->{'Requestid'} || $args->{'show_id'} || $args->{'msid'};
        # FIXME FIXME FIXME: не должно быть никаких qx `` system и т.д.!!!!
        # это потенциальный RCE
        # файлы надо читать самим перлом !!!!
        if ($Requestid && $Requestid =~ /^[-0-9a-z.]+$/i) {
            # Хоть у нас и строгая регулярка но так как используется qx то
            # эскейпим потенциальные shell уязвимости
            my @files = (
                MordaX::Conf->get('LogDir') . "/blockdisplay." . $date . "??",
                MordaX::Conf->get('LogDir') . "/node.blockdisplay." . $date,
            );
            $Requestid =~ s,','"'"',g;

            my $command = "fgrep '" . $Requestid . "' " . join(' ', @files);
            my $line    = qx{$command};
            $tskv_data = Utils::Tskv::process_line($line);
            #dmp( $tskv_data );
            my $blocks = $tskv_data->{blocks};
            my @raw = split(/\\t/, $tskv_data->{blocks});
            my $name;
            my $data = {};
            for (my $i = 0; $i < @raw; $i++) {
                my $name = $raw[$i];
                $data->{$name} = {};
                push @v1data, $name;

                my $size = $raw[$i + 1];
                for (my $j = 0; $j < $size; $j++) {
                    my $in = $raw[$i + 2 + $j];
                    my ($key, $val) = split(/=/, $in, 2);
                    if ($val eq 'UNDEF') {
                        $val = undef;
                    } elsif ($val =~ /,/) {
                        $val = {map { $_ => 1 } split(/,/, $val)};
                    }
                    $data->{$name}->{$key} = $val;
                }

                $i += 1 + $size;

            }
            $tskv_data->{blocks} = $data;
        }

        my $output;
        if ($args->{v} == 2) {
            $output = JSON::XS->new->canonical(1)->pretty(1)->allow_unknown(1)->encode($tskv_data);
        } else {
            $output = JSON::XS->new->canonical(1)->pretty(1)->allow_unknown(1)->encode(\@v1data);
        }
        return $output;
    };

1;
