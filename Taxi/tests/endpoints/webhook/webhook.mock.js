const config = require('../../../server/config');

module.exports = {
    createPR: {
        title: 'Test',
        head: 'hiring-frontend-dev-api/TXIFM-58-3',
        base: 'master',
        body: 'https://st.yandex-team.ru/TXIFM-58',
    },
    labelRC: {
        common: {
            gh: {
                owner: config.GH_FM_REPO_OWNER,
                repo: config.GH_FM_REPO_NAME,
            },
            ticket: 'TXIFM-58',
        },
        wrong: {
            gh: {
                owner: config.GH_FM_REPO_OWNER,
                repo: config.GH_FM_REPO_NAME,
            },
            ticket: 'TXIFM-58123',
        },
    },
    unstableLabel: 'deploy:testing',
    wrongUnstableLabel: 'testing123',
    PRTemplate: `{{BODY}}
Service: {{SERVICE}}

## Tickets
{{TICKETS}}

## Profits
* <img src='https://wiki.s3.yandex.net/yandex-wiki-www/v10.148.0/intranet-production-favicon-16.png' width='20' height='20' align='absmiddle'></img> [**Wiki**](https://wiki.yandex-team.ru/taxi/efficiency/dev/frontend/rtc/fast-create-service/)
* <img src='https://assets.github.yandex-team.ru/favicon-ent.ico' width='20' height='20' align='absmiddle'></img> [**Packages**](https://github.yandex-team.ru/taxi/frontend-monorepo/packages)
* <img src='https://assets.github.yandex-team.ru/favicon-ent.ico' width='20' height='20' align='absmiddle'></img> [**Services**](https://github.yandex-team.ru/taxi/frontend-monorepo/services)
{{LINKS}}
    `,
    onOpenPREvent: {
        action: 'opened',
    },
    onEditPREvent: {
        action: 'edit',
    },
    PRBodyAfterUpdate: `Service: hiring-frontend-dev-api

## Tickets
1. https://st.yandex-team.ru/TXIFM-58-3

## Profits
* <img src='https://wiki.s3.yandex.net/yandex-wiki-www/v10.148.0/intranet-production-favicon-16.png' width='20' height='20' align='absmiddle'></img> [**Wiki**](https://wiki.yandex-team.ru/taxi/efficiency/dev/frontend/rtc/fast-create-service/)
* <img src='https://assets.github.yandex-team.ru/favicon-ent.ico' width='20' height='20' align='absmiddle'></img> [**Packages**](https://github.yandex-team.ru/taxi/frontend-monorepo/packages)
* <img src='https://assets.github.yandex-team.ru/favicon-ent.ico' width='20' height='20' align='absmiddle'></img> [**Services**](https://github.yandex-team.ru/taxi/frontend-monorepo/services)
* <img src="https://teamcity.taxi.yandex-team.ru/img/icons/teamcity.svg" width="20" height="20" align="absmiddle"></img> [**Service Unstable Build**](https://teamcity.taxi.yandex-team.ru/viewType.html?buildTypeId=YandexTaxiProjects_Infranaim_Frontend_NewFlowTest&branch_YandexTaxiProjects_Infranaim_Frontend=hiring-frontend-dev-api)
* <img src="https://nanny.yandex-team.ru/favicon.ico" width="20" height="20" align="absmiddle"></img> [**Service Nanny (testing)**](https://nanny.yandex-team.ru/ui/#/services/catalog/taxi_frontend-dev-api_testing/)
* <img src="https://nanny.yandex-team.ru/favicon.ico" width="20" height="20" align="absmiddle"></img> [**Service Nanny (unstable)**](https://nanny.yandex-team.ru/ui/#/services/catalog/taxi_frontend-dev-api_unstable/)
    `,
    PRWithLabel: {
        number: 1679,
        title: 'INFRANAIM: Test',
        user: {
            login: 'msmazhanov',
        },
        body: '{{BODY}}\r\nService: {{SERVICE}}\r\n\r\n## Tickets\r\n{{TICKETS}}\r\n\r\n## Profits\r\n* <img src="https://wiki.s3.yandex.net/yandex-wiki-www/v10.148.0/intranet-production-favicon-16.png" width="20" height="20" align="absmiddle"></img> [**Wiki**](https://wiki.yandex-team.ru/taxi/efficiency/dev/frontend/rtc/fast-create-service/)\r\n* <img src="https://assets.github.yandex-team.ru/favicon-ent.ico" width="20" height="20" align="absmiddle"></img> [**Packages**](https://github.yandex-team.ru/taxi/frontend-monorepo/packages)  \r\n* <img src="https://assets.github.yandex-team.ru/favicon-ent.ico" width="20" height="20" align="absmiddle"></img> [**Services**](https://github.yandex-team.ru/taxi/frontend-monorepo/services)\r\n{{LINKS}}\r\n',
        labels: [
            {
                name: 'deploy:testing',
            },
        ],
        head: {
            ref: 'hiring-frontend-dev-api/TXIFM-58-3',
        },
        base: {
            repo: {
                name: 'frontend-monorepo',
                owner: {
                    login: 'robot-yataxi-daniel',
                },
            },
        },
    },
    deployMessageInfo: {
        links: {
            golovan: 'https://yasm.yandex-team.ru/panel/robot-taxi-clown.nanny_taxi_cool_service_stable',
            grafana: 'https://grafana.yandex-team.ru/d/someuuid/nanny_taxi_cool_service_stable',
            kibana: 'https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=%28filters:!%28%29%29&_a=%28columns:!%28_source%29,filters:!%28%28"$state":%28store:appState%29,meta:%28alias:!n,disabled:!f,index:f8e70880-c75c-11e9-8a12-ddb2ef5a51ea,key:ngroups,negate:!f,params:%28query:taxi_cool_service_stable%29,type:phrase,value:taxi_cool_service_stable%29,query:%28match:%28ngroups:%28query:taxi_cool_service_stable,type:phrase%29%29%29%29,%28"$state":%28store:appState%29,meta:%28alias:!n,disabled:!f,index:f8e70880-c75c-11e9-8a12-ddb2ef5a51ea,key:level,negate:!f,params:!%28ERROR,WARNING%29,type:phrases,value:"ERROR,+WARNING"%29,query:%28bool:%28minimum_should_match:1,should:!%28%28match_phrase:%28level:ERROR%29%29,%28match_phrase:%28level:WARNING%29%29%29%29%29%29%29,index:f8e70880-c75c-11e9-8a12-ddb2ef5a51ea,interval:auto,query:%28language:kuery,query:""%29,sort:!%28"@timestamp",desc%29%29',
            nanny: 'https://nanny.yandex-team.ru/ui/#/services/catalog/taxi_cool_service_stable/',
            service_deploy: 'https://service.yandex.net/changelog',
        },
        meta: {
            changelog: '{\"tickets\": [\"TXIFM-389\"]}',
            cluster_type: 'nanny',
            direct_name: 'taxi_cool_service_stable',
            docker_image: 'taxi/rtc-stub/0.0.1',
            environment: 'stable',
            hosts: [
                'taxi-frontend-yandex.taxi.yandex.net',
            ],
            service_name: 'taxi-frontend-yandex',
        },
    },
    postDeployTicket1: '{\"tickets\": [\"FMTAXIRELTEST-451\"], \"arcanum_pull_request\": \"2487112\", \"build_link\": \"https://teamcity.taxi.yandex-team.ru/viewLog.html?buildId=7510777&tab=buildResultsDiv&buildTypeId=YandexTaxiProjects_Frontend_Monorepo_Customs_CustomUnstable\"}',
    postDeployTicket2: '{\"tickets\": [\"FMTAXIRELTEST-452\"], \"arcanum_pull_request\": \"2487112\", \"build_link\": \"https://teamcity.taxi.yandex-team.ru/viewLog.html?buildId=7510777&tab=buildResultsDiv&buildTypeId=YandexTaxiProjects_Frontend_Monorepo_Customs_CustomUnstable\"}',
    postDeployTicket3: '{\"tickets\": [\"FMTAXIRELTEST-453\"], \"arcanum_pull_request\": \"2487112\", \"build_link\": \"https://teamcity.taxi.yandex-team.ru/viewLog.html?buildId=7510777&tab=buildResultsDiv&buildTypeId=YandexTaxiProjects_Frontend_Monorepo_Customs_CustomUnstable\"}',
    postDeployTicket4: '{\"tickets\": [\"FMTAXIRELTEST-454\"], \"arcanum_pull_request\": \"2487112\", \"build_link\": \"https://teamcity.taxi.yandex-team.ru/viewLog.html?buildId=7510777&tab=buildResultsDiv&buildTypeId=YandexTaxiProjects_Frontend_Monorepo_Customs_CustomUnstable\"}',
    postDeployError: 'FMTAXIRELTEST-454',
};
