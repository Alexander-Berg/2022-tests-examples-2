package MordaTest;

# Enviroment to run morda fuctions
use lib::abs qw(../../lib/ ../../wbox/lib ../../wdgt/lib);
use lib "/opt/www/bases/";

#$main::etcpath = lib::abs::path('../../etc/');

use strict;
use utf8;

use Data::Dumper;
use JSON::XS;
use File::Spec;

use URI::http;

use MP::Logit qw(dmp logit);
use MordaX::Conf;
use MordaX::Config;
use MordaX::Cache;
use MordaX::Data_load;

#use InitBase;
#use InitUtils;

use Cache::Memcached::Fast;
use MordaX::CacheFaker;

#require geobase_limited;

#use WBWI::Input; # this is not mistypes
#use WBOX::Utils;
#use WBOX::Requester;
#use WBOX::Model::Widget;

#use  WDGT::Conf;
#use MordaX::Tmpl;

$MordaX::Config::TestRun = 1;

$MordaX::Errorlog::setuplogging{debug}  = 0;
$MordaX::Errorlog::setuplogging{config} = 0;

#?use JSTemplate;
$JSTemplate::disabled = 1;

use Pfile;

no strict 'refs';
if (%{'Test::More::'} and Test::More->can('note')) {
    &Test::More::note("overwriting configs");
}
else {
    logit('debug', "overwriting configs");
}

$Pfile::logpath = lib::abs::path("./varlog");
MordaX::Conf->new()->set('TemplatesCompileDir', lib::abs::path("./tt2tmp"));
if (1 == 0) {
    MordaX::Conf->new()->set('BasesDir', lib::abs::path("./bases"));
}

if (%{'Test::More::'} and Test::More->can('note')) {
    &Test::More::note('compile dir', MordaX::Conf->get('TemplatesCompileDir'));
}
else {
    logit('debug', 'compile dir', MordaX::Conf->get('TemplatesCompileDir'));
}
use strict 'refs';

#InitMorda is heavy and ugly
#? MordaX::Data_load::init_datas();
#require InitMorda;
MordaX::CacheFaker::bind(MordaX::Cache->new());
#use Templater;

#log on
$MordaX::Errorlog::setuplogging{debug} = 1;
#use Geo;

#require geobase;

unless (MordaX::Conf->new()) {
    my $ts = localtime();
    print STDERR
      "[$ts] [mordax] [startup] Config object initialization failed, apache isn't started. Check mordax config files\n";
    exit(1);
}

#my ($tmpl_dir) = MordaX::Conf->get('TemplatesDir');

=wat
# Template Toolkit II object
$MordaX::Tmpl::tt = Templater->new({
        Provider => {
            INCLUDE_PATH => $tmpl_dir,
#        COMPILE_EXT => '.compiled',
#        COMPILE_DIR => $tmpl_cache,
          }
    }
);

unless ($MordaX::Tmpl::tt) {
    print STDERR "Template toolkit object initialization failed\n";
    #exit(1);
}
=cut

sub load_dump {
    my $file = shift;
    return undef unless -f $file;

    my $VAR1;
    eval {
        my $var = '';
        open(DUMP_IN, $file);
        while (<DUMP_IN>) {
            $var .= $_;
        }
        close(DUMP_IN);
        $VAR1 = eval($var);
        #|| croak $@;
        #warn $VAR1;
    };
    if ($@) {
        #    croak;
        warn "Error in evaluating dump: $@\n";
    }
    return $VAR1;
}

package WBWI::Input;

sub new_doomie {
    my $class = shift;
    my $this  = {
        Cookies    => {},
        AllCookies => '',
        Domain     => 'yandex.ru',
        Hostname   => 'yandex.ru',
        Uri        => '/',
        Rawquery   => '',
        Query      => {},
        Postdata   => {},
        Method     => 'POST',
        Rawbody    => '',
        ip_from    => '127.0.0.1',
        ip_prox    => '',
        'utf-8'    => 1,
        'cp1251'   => 0,
    };

    bless $this, $class;
    return $this;
}

1;
