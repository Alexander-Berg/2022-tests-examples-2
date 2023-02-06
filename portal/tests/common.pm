
use lib::abs qw(../lib/ ../../wbox/lib ../../wdgt/lib ../../lib ../../wdgt/lib ../scripts);

#warn "LIB PATH: " . lib::abs::path('../etc');

#$main::etcpath = '../etc/';

use strict;
use utf8;

use Data::Dumper;
use JSON::XS;
use File::Spec;
use Template;

#use InitBase;

use WBWI::Input;    # this is not mistypes
use WBOX::Utils;
use WBOX::Requester;
use WBOX::Model::Widget;
use WADM::Index;
use WADM::Conf;
use FakeInput;
use MordaX::Data_load;
use MordaX::Conf;
use MordaX::Config;

use Exporter;
use vars qw(@ISA @EXPORT);
@ISA    = qw(Exporter);
@EXPORT = qw(get save add_to_catalog add_to_regional read_data_file);

eval {
    MordaX::Conf->new()->set('TemplatesCompileDir', lib::abs::path("./tt2tmp"));
    WADM::Conf->new()->set('TemplatesCache', lib::abs::path("./tt2tmp"));

    $MordaX::Config::DevInstance = 1;

    MordaX::Data_load::load_static_exports();
};

sub get {
    return WADM::Index::widget_by_wid(@_);
}

sub save {
    $WBOX::Requester::requester->widget_update(
        shift,
        WADM::Utils::get_replic_retry_pattern(),
        2
    );
}

sub add_to_catalog {
    my $w        = shift;
    my %cat_data = (
        'wid'   => $w->id(),
        'uid'   => $w->uid(),
        'wtype' => $w->type(),
        'title' => $w->title(),
        'wdata' => $w->get(),
    );
    wboxdb_request(\%cat_data, 'addcatalogwidget', 'master');
    $w->catflag('inside');
    save($w);
}

sub add_to_regional {
    my $w        = shift;
    my %cat_data = (
        'wid'   => $w->id(),
        'uid'   => $w->uid(),
        'wtype' => $w->type(),
        'title' => $w->title(),
        'wdata' => $w->get(),
    );
    wboxdb_request(\%cat_data, 'addregionalwidget', 'master');
    $w->regflag('inside');
    save($w);
}

sub read_data_file {
    my $id   = shift;
    my $path = lib::abs::path("./data");
    my $file = File::Spec->catfile($path, $id);

    unless (-f $file) {
        die("data file: $file, not found!");
        return undef;
    }

    open my $fh, '<', $file;
    local $/ = undef;
    my $data = <$fh>;
    close $fh;

    return $data;
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

{
    no warnings;
    *WADM::Index::r200 = sub {
        return $_[1];
    };
#    *WADM::Index::r500 = sub {
#        warn "STATUS 500\n";
#        return 'error';
#    };
    sub WADM::Index::r500($$) {
        warn "STATUS 500\n";
        return 'error';
    }
    *WADM::Index::r302 = sub {
        return $_[1];
    };
    *WADM::Index::r404 = sub {
        warn "STATUS 404\n";
        return 'error';
    };
}
# WARNING package WBWI::Input;

1;
