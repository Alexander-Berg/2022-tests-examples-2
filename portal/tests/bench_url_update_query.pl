#!/usr/bin/perl

use lib::abs qw(../lib);
use rules;
use Benchmark;
use MordaX::Utils;

Benchmark::cmpthese(-3, {
    'old' => sub {
        MordaX::Utils::url_update_query_slow('ya.ru', 1=>2);
    },
    'new' => sub {
        MordaX::Utils::url_update_query_fast('ya.ru', 1=>2);
    },
    'url_param_glue' => sub {
        MordaX::Utils::url_param_glue('ya.ru', "1=2");
    },

}, 'all');

Benchmark::cmpthese(-3, {
    'old_long' => sub {
        MordaX::Utils::url_update_query_slow(
            'https://yandex.ru/portal/api/search/2?from=multimorda&fix=&app_id=ru.yandex.searchplugin&app_platform=android&app_version=9000500&did=441fca749cc11653fcee8bf3ed935477&uuid=a0ff0ef93281469f9e077d9de7617a4e',
            'appsearch_header' => 1
        );
    },
    'new_long' => sub {
        MordaX::Utils::url_update_query_fast(
            'https://yandex.ru/portal/api/search/2?from=multimorda&fix=&app_id=ru.yandex.searchplugin&app_platform=android&app_version=9000500&did=441fca749cc11653fcee8bf3ed935477&uuid=a0ff0ef93281469f9e077d9de7617a4e',
            'appsearch_header' => 1
        );
    },
    'url_param_glue_long' => sub {
        MordaX::Utils::url_param_glue('https://yandex.ru/portal/api/search/2?from=multimorda&fix=&app_id=ru.yandex.searchplugin&app_platform=android&app_version=9000500&did=441fca749cc11653fcee8bf3ed935477&uuid=a0ff0ef93281469f9e077d9de7617a4e', "appsearch_header=1");
    },
}, 'all');
