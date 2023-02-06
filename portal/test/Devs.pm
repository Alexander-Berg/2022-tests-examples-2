package Test::Devs;
use rules;
use MP::Stopdebug;

use lib::abs qw(../);

use MordaX::Logit qw(dmp logit);
use MordaX::Utils;
use MordaX::Config;
use TestHelper qw(no_register);

my $mordas_root = '/opt/www/';
my $wait_max    = 10;

sub run_get_oneline(@) {
    my $ret = (`@_`)[0];
    $ret =~ s/\s+$//;
    return $ret;
}

sub handler {
    my ($req, $data, $post) = @_;

    my $page = $data->{'Page'};
    if (opendir(my $dh, $mordas_root)) {
        my @devs;
        while (my $instance_folder = readdir $dh) {
            next if /^\./;
            my $instance = {};
            $instance->{'full'} = $mordas_root . $instance_folder;
            next if not -e $instance->{'full'} . '/.git';
            $instance->{'name'} = $instance_folder;
            $instance->{'name'} =~ s/^morda-//;
            ($instance->{'name_sort'} = $instance->{'name'}) =~ s/\D+/\./g;
            $instance->{'name_sort'} =~ s/^\D+//;
            $instance->{'host_nodomain'}    = $instance->{'name'} . '.wdevx.yandex.';
            $instance->{'host_team'}        = $instance->{'name'} . '.wdevx.yandex-team.ru';
            $instance->{'host_nodomain_ya'} = $instance->{'name'} . '.wdevx.ya.';
            $instance->{'host'}             = $instance->{'host_nodomain'} . 'ru';
            $instance->{'host_www'}         = 'www-' . $instance->{'host'};
            $instance->{'user'}             = (getpwuid((stat "$instance->{full}/.git/index")[4]))[0];

            my $proto = 'https://';
            _add_sites($instance, $proto);

            $instance->{'unfinished'} = 1;
            push @devs, $instance;
        }
        closedir $dh;
        $page->{'devs'} = [sort { MordaX::Utils::cmpversion($a->{'name_sort'}, '<=>', $b->{'name_sort'}) } @devs];
    }

    my $time_max = time() + $wait_max;
    foreach my $instance (@{ $page->{'devs'} }) {
        $instance->{'commit'}   = run_get_oneline(qq{git --git-dir=$instance->{full}/.git --work-tree=$instance->{full} rev-parse HEAD});
        $instance->{'describe'} = run_get_oneline(qq{git --git-dir=$instance->{full}/.git --work-tree=$instance->{full} describe});
        my @git_st = `git --git-dir=$instance->{full}/.git --work-tree=$instance->{full} status --porcelain --branch --untracked-files=no`;
        my $st    = shift @git_st;
        if ($st =~ s/^## (.+)$//m) {
            $instance->{'branch'} = $1;
            $instance->{'branch'} =~ s{(\S+)\.\.\.\S+/\1}{$1};
            $instance->{'status'} = $1 if $instance->{'branch'} =~ s/\s+(.*)$// and $1;
        }

        if (@git_st > 10) {
            $instance->{'git_st_more'} = join '', splice @git_st, 10;
        }
        $instance->{'git_st'} = join '', @git_st;
        #$git_st =~ /^# On branch (.+)$/m;
        #$instance->{git_st} =~ s/^## (.+)\.\.\.(\S+)$//m;
        $instance->{'task'} = uc $1 if $instance->{'branch'} =~ /(home-\d+)/i;
        $instance->{'git_age'} = time() - $^T + 86400 * -M "$instance->{full}/.git/index";
        $instance->{'git_age_days'} = sprintf '%.1f', $instance->{'git_age'} / 86400;

        delete $instance->{'unfinished'};
        if (time() > $time_max) {
            $page->{'unfinished'} = $wait_max + time() - $time_max;
            last;
        }
    }

    return MordaX::Output::r200json($req, $data) if $req->{Getargshash}{json};
    return TestHelper::resp($req, 'test/devs.html', $data);
}

sub _add_sites {
    my ($instance, $proto) = @_;

    $instance->{'sites'} = [
        {
            'name' => 'madm',
            'url'  => $proto . 'madm-' . $instance->{'host_team'}
        }, {
            'name' => 'wadm',
            'url'  => $proto . 'wadm-' . $instance->{'host_team'}
        }, {
            'name' => 'test',
            'url'  => $proto . 'www-' . $instance->{'host'} . '/test/'
        },
        (map { { 'name' => 'www-' . $_, 'url' => $proto . 'www-' . $instance->{'host_nodomain'} . $_ } } sort keys %MordaX::Config::EnabledZones),
        (map { { 'name' => 'touch-' . $_, 'url' => $proto . 'www-' . $instance->{'host_nodomain'} . $_ . '/?content=touch' } } qw(ru com.tr com)),
        (
            map {
                {
                    'name' => 'mob-' . $_,
                    'url'  => $proto . 'www-' . $instance->{'host_nodomain'} . $_ . '/?content=mob'
                }
              } qw(ru com.tr com)
          ), (
            map {
                {
                    'name' => 'tel-' . $_,
                    'url'  => $proto . 'tel-' . $instance->{'host_nodomain'} . $_ . '/'
                }
              } qw(ru)
          ), (
            map {
                {
                    'name' => 'tv-' . $_,
                    'url'  => $proto . 'www-' . $instance->{'host_nodomain'} . $_ . '/?content=tv'
                }
              } qw(ru)
          ),
        (map { { 'name' => 'yaru' . $_, 'url' => $proto . $instance->{'host_nodomain_ya'} . $_ . '/' } } qw(ru)),
        (map { { 'name' => 'all-' . $_, 'url' => $proto . 'www-' . $instance->{'host_nodomain'} . $_ . '/all' } } qw(ru ua by kz com.tr)),
        (map { { 'name' => 'api1-' . $_, 'url' => $proto . 'www-' . $instance->{'host_nodomain'} . $_ . '/portal/api/search/1/' } } qw(ru)),
        (map { { 'name' => 'api2-' . $_, 'url' => $proto . 'www-' . $instance->{'host_nodomain'} . $_ . '/portal/api/search/2/' } } qw(ru)),
        (map { { 'name' => '404-' . $_, 'url' => $proto . 'www-' . $instance->{'host_nodomain'} . $_ . '/sl/notexistinguuurl' } } qw(ru ua com.tr com)),
    ];
}

1;
