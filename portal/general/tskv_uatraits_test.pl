#!/usr/bin/perl

use lib::abs qw( ../lib);
use common::sense;

#use InitBase;

use MordaX::Uatraits;
use MordaX::Req;
use MordaX::Mobile;
use MordaX::Input;
use MordaX::Conf;
use Utils::Tskv;

use MordaX::Logit qw(logit dumpit);
InitUtils::init_phonedetect();
MordaX::Uatraits::init();

use HTTP::Headers;

logit('debug', 'hello world how are you feeling');

my $file = MordaX::Conf->get('LogDir') . "/morda-dev49.access_log.20120127";

my $false_triggered_file = "ua_false_trigered.txt";
my $not_triggered_file   = "ua_not_trigered.txt";
my $unknown_ua_file      = 'ua_unknonwn.txt';

if ($ARGV[0]) {
    $file = $ARGV[0]
}
if ($ARGV[1]) {
    $false_triggered_file = File::Spec->catfile($ARGV[1], $false_triggered_file);
    $not_triggered_file   = File::Spec->catfile($ARGV[1], $not_triggered_file);
    $unknown_ua_file      = File::Spec->catfile($ARGV[1], $unknown_ua_file);
}
logit('debug', "usage $! [tskv_path.txt [ dir_to store files ]]");

my $recs = Utils::Tskv::read_file($file);
logit('debug', "log has: " . scalar @$recs . "records");
$mordax::EnableMobileDetection{big} = 1;

open(NT,  ">>$not_triggered_file");
open(FT,  ">>$false_triggered_file");
open(UNK, ">>$unknown_ua_file");

open(IN, $file);

my (%NT, %FT, %UNK, %KNWN);
while (<IN>) {
    chomp;
    my $rec = {};
    (undef, undef, $rec->{user_agent}, $rec->{wap_profile}) = split(/\t/, $_);
    #($rec->{user_agent}, $rec->{wap_profile} ) = split(/\t/, $_);
    my $ua = $rec->{user_agent};
    if ($KNWN{$ua}) {
        next;
    }
    $KNWN{$ua} = 1;

#for my $rec ( @$recs ){}
    my $h = fake_headers($rec->{user_agent}, $rec->{wap_profile});
    my $req = MordaX::Req->new();
    $req->{UserAgent} = $rec->{user_agent};

    #--
    unless ($req->{UserAgent}) {
        #dumpit( 'NO UA: ', $rec );
        next;
    }

    my $userdevice = MordaX::Mobile::detect_mobile($req, 'x', $h);
    MordaX::Mobile::deviceplatform($req, $userdevice);    # HOME-6720

    my $ua = $rec->{user_agent};
    my $ua_desc = MordaX::Uatraits::detect($req, $rec->{user_agent});
    $req->{BrowserDesc} = $ua_desc;

    if ($req->{isMobile}) {
        if (!$ua_desc->{isMobile}) {
            logit('warning', "not triggered on $rec->{user_agent}");
            unless ($NT{$ua}) {

                print NT $req->{UserAgent} . "\n";
            }

        }
    } else {
        if ($ua_desc->{isMobile}) {

=x
            dumpit( $userdevice, 
                $h, 
                #$req, 
                $ua_desc
            );
=cut

            logit('warning', "false triggered on $rec->{user_agent}");
            print FT $req->{UserAgent} . "\n";
        }
    }
    next;
    my $set = MordaX::Uatraits::fillin_mobile_flags($req);
    #dumpit( $ua_desc,$req, $set );
    next;

    if (MordaX::Uatraits::find_unknown_ua(undef, $ua, $ua_desc)) {
        print UNK $ua . "\n";
    }

    #last one
    next if $ua =~ /Windows-RSS-Platform/;

    my $input = {
        UserAgent => $ua,
        Request   => {
            UserAgent   => $ua,
            BrowserDesc => $ua_desc,
        },
    };
    bless($input, "MordaX::Input");
    $input->fillin_browser();

    my $b1 = $input->{Request};
    my $b2 = $b1->{BrowserTmp};

    my $err = 0;
    for (qw/isMSIE isOpera MSIE FireFox Chrome/) {
        if (($b1->{$_} || '') ne ($b2->{$_} || '')) {
            #  if( $_ eq 'MSIE' and ( $b1->{$_} eq '7.0')  and $b2->{$_} ){
            #    next;
            #}

            $err = 1;
            logit('debug', "browser dmg: $_ : original: " . $b1->{$_} . "new: " . $b2->{$_});
        }
    }
    if ($err) {
        logit('debug', "ua: $ua");
        dumpit($b1, $b2);
    }

}

sub fake_headers {
    my ($ua_desc, $wap) = @_;
    my $h = {
        'User-Agent'    => $ua_desc,
        'X-Wap-Profile' => $wap,
    };
    return $h;
}

