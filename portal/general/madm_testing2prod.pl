#!/usr/bin/perl

use lib::abs qw(./ ../lib);
use rules;

use File::stat;

use MD::MADM::Source;
use MP::Logit;
use MordaX::Options;
use MADM::Index;
use MordaX::Conf;
use MordaX::Req;
use MordaX::Data_load;

use constant DEFAULT_TIMEOUT => 3;  # Время ожидания выкладки в production из testing после обновления файла (в минутах)
                                    # Может быть переопределено опцией

my $export_name = $ARGV[0];

unless ($export_name) {
    logit('warning', 'No export file specified');
    exit 0;
}

MD::MADM::Source::MADMSrc->load_exports(qw(options));

exit 0 if MordaX::Options::options('covid_speed_auto_disable') && ($export_name eq 'covid_speed');

my $from_file = MADM::Index::file_full('testing', $export_name);

unless (-e $from_file) {
    exit 0;
}

my $timeout = MordaX::Options::options('covid_speed_autoupdate_timeout') // DEFAULT_TIMEOUT;
exit 0 if $timeout <= 0; # Автообновление выключено

my $source_mtime = stat($from_file)->mtime;

my $to_file = MADM::Index::file_full('production', $export_name);

my $target_mtime = 0;
if (-e $to_file) {
    $target_mtime = stat($to_file)->mtime;
}

exit 0 if $source_mtime - $target_mtime < $timeout * 60; # Файл в production не достаточно старый относительно testing

if (!MordaX::Options::options('no_infra')) {
    my $infra_conf = MordaX::Conf->get('infra');

    if ($infra_conf->{send_madm_events}) {
        my $params = {
            title         => MADM::Index::get_title_from_diff({}, '', $export_name),
            description   => "Released by cron
Trunk: https://madm.yandex-team.ru/edit?export_file=$export_name&stage=production",
            serviceId     => int($infra_conf->{madm_service_id}),
            environmentId => int($infra_conf->{madm_env_id}),
            startTime     => time,
            finishTime    => time + 180,
            severity      => 'minor',
            type          => 'maintenance',
        };
        MordaX::Infra::send_event_to_infra(MordaX::Req->new(), $params);
    }
}

if (-e $to_file) {
    MADM::Index::move($to_file, MADM::Index::file_full('history', $export_name . '.' . int(time())));
}

MordaX::Data_load::init_datas();                # perversion

my $file_data = MADM::Index::data_read($from_file);
$file_data->{stage} = 'production';
$file_data = MADM::Index::prepare_fields($file_data);
$file_data->{options} = MADM::ExportTypes::format($export_name, 'options');

MADM::Index::write_ready($file_data, { 'time' => $source_mtime });
MADM::Index::move($from_file, $to_file);

exit 0;
