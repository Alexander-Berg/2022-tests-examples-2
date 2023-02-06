#!/usr/bin/perl

use common::sense;
use common;

use Test::More;

use WADM::WidgetMailer;
use WADM::Index;
use WADM::Conf;
use MordaX::Config;
use utf8;

$MordaX::Config::DevInstance = 1;

use_ok('WADM::WidgetMailer');

#my $widget = get(22009);     #zhx
#my $widget = get(64357);    # slight
#my $widget = get(66778);    # k.yukhnevich@yandex.ru
my $widget = get(73887);    #bmert

ok($widget, 'widget loaded');

my $tmpl_path = WADM::Conf->get('Templates');
ok(-d $tmpl_path,                         'tmpl presents: ' . $tmpl_path);
ok(-d $tmpl_path . '/l10n',               'tmpl l10n presents');
ok(-f $tmpl_path . '/l10n/blocks.ru.tt2', 'tmpl ru blocks  presents');
ok(-f $tmpl_path . '/l10n/mails.ru.tt2',  'tmpl ru mails  presents');

#CAT Falg
ok(
    WADM::WidgetMailer->mailit(
        action => 'catflag:inside',
        widget => $widget,
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action => 'catflag:reject',
        widget => $widget,
        reason => 'просто так',
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action => 'catflag:outside',
        widget => $widget,
        reason => 'просто так аутсайтд',
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action => 'catflag:avalible',
        widget => $widget,
      )
);
$widget->in_regional(1);
ok(
    WADM::WidgetMailer->mailit(
        action => 'catflag:avalible',
        widget => $widget,
      )
);

#REG-flag
ok(
    WADM::WidgetMailer->mailit(
        action => 'regflag:inside',
        widget => $widget,
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action => 'regflag:reject',
        widget => $widget,
        reason => 'Регионалка говорит вам Ни-Ни',
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action => 'regflag:outside',
        widget => $widget,
        reason => 'региональная просгрма для вас более не доступна Ха Ха Ха',
      )
);
#actflag
ok(
    WADM::WidgetMailer->mailit(
        action => 'actflag:banned',
        widget => $widget,
        reason => 'досвидания мой любимый город',
      )
);

#dont work
$widget->in_regional(0);
ok(
    WADM::WidgetMailer->mailit(
        action => 'dont_work',
        widget => $widget,
        reason =>
          'досвидания мой любимый город, труба забиласть виджет не паштет',
        delete_date => '2010-01-12',
      )
);
$widget->in_catalog(1);
ok(
    WADM::WidgetMailer->mailit(
        action => 'dont_work',
        widget => $widget,
        reason => 'досвидания, убедитесь что из каталога виджет удален',
        #Are you SHURE
        #excluded_from => { catalog => 1 },
        delete_date => '2010-01-12',
      )
);

$widget->in_catalog(0);

ok(
    WADM::WidgetMailer->mailit(
        action => 'dont_work:heavy',
        widget => $widget,
        reason => 'ла ля ',
      )
);

#--------------------------------------------------
#virus flag
ok(
    WADM::WidgetMailer->mailit(
        action        => 'virus:found',
        widget        => $widget,
        reason        => 'вирус нашли, программы ликвидировали',
        excluded_from => {regional => 1},
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action => 'virus:found',
        widget => $widget,
        reason => 'вирус нашли',
      )
);

ok(
    WADM::WidgetMailer->mailit(
        action => 'virus:clean',
        widget => $widget,
        reason => 'виджет почистился ',
      )
);
$widget->in_catalog(1);
ok(
    WADM::WidgetMailer->mailit(
        action => 'virus:clean',
        widget => $widget,
        reason => 'виджет почистился, программы вернули ',
      )
);
$widget->in_catalog(0);
#-------------------------------------------------- -
#
ok(
    WADM::WidgetMailer->mailit(
        action       => 'warning',
        widget       => $widget,
        reason       => 'предупреждение китайское',
        exclude_date => '2011-06-07',
      )
);

#------------------------------------------------------
ok(
    WADM::WidgetMailer->mailit(
        action       => 'rss:warn',
        widget       => $widget,
        exclude_date => '2011-06-07',
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action        => 'rss:rotten',
        widget        => $widget,
        excluded_from => {
            regional => 1,
          }
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action => 'rss:rotten',
        widget => $widget,
      )
);

#------------------------------------------------------
ok(
    WADM::WidgetMailer->mailit(
        action => 'rss:recover',
        widget => $widget,
        reason => 'предупреждение китайское',
      )
);
$widget->in_catalog(1);
ok(
    WADM::WidgetMailer->mailit(
        action => 'rss:recover',
        widget => $widget,
        reason => 'предупреждение китайское',
      )
);
$widget->in_catalog(0);
#--------------------------------------------------

ok(
    WADM::WidgetMailer->mailit(
        action      => 'src:notfound',
        widget      => $widget,
        delete_date => '2011-06-07',
      )
);
ok(
    WADM::WidgetMailer->mailit(
        action        => 'src:notfound',
        widget        => $widget,
        delete_date   => '2011-06-07',
        excluded_from => {
            regional => 1,
          }
      )
);

done_testing();
