import sinon from 'sinon';
import {Project} from '../lib/config';
import type {Config, ComponentLike} from '../lib/config';
import type {CommitInfo, DeployRule} from '../lib/config-types';
import type {IssueProvider} from '../lib/startrek';
import {TkitGraph} from '../lib/tkit-graph';
import type {WorkflowInt} from '../lib/workflow';
import {SandboxResource} from '../lib/sandbox';

export function getComponentMock(
    name: string,
    haveS3: boolean,
    haveOther: boolean,
    haveChanges = true): ComponentLike {
    const deploy: DeployRule[] = [];
    if (haveS3) {
        deploy.push({
            path: '/path/to/' + name,
            s3path: '/s3/path/' + name
        });
    }
    if (haveOther) {
        deploy.push({
            path: '/path/to/' + name,
            resource: 'TYPE_' + name.toUpperCase()
        });
    }
    return {
        getName: () => name,
        getDeploy: () => deploy,
        hasFiles: () => haveChanges,
        getRoot: () => '',
        getCommand: () => 'eccho "fake command"'
    };
}

export function getProjectConfigMock() {
    return new Project('morda', {
        components: [],
        startrek: {
            releaseQueue: 'HOME',
            skip: []
        }
    }, {} as Config);
}

export function getWorkflowMock(projectConfig?: Project): WorkflowInt {
    const mock = {
        getComponentWorkCopy: (name) => '/path/to/wrk/' + name,
        getComponentBuildName: (name) => 'step-' + name,
        getCommits: (): Promise<CommitInfo[]> => {
            return Promise.resolve([
                {
                    mark: '*',
                    hash: '1236',
                    url: '/fakecommit/1236',
                    message: 'QWE-117: normal commit'
                },
                {
                    mark: '*',
                    hash: '1235',
                    url: '/fakecommit/1235',
                    message: 'QWE-111: 2nd normal commit'
                }
            ]);
        },
        getProjectConfig: () => {
            return projectConfig || getProjectConfigMock();
        },
        getDiff: sinon.stub(),
        getTicket: sinon.stub()
    };

    sinon.spy(mock, 'getComponentBuildName');

    return mock;
}

export function getIssueProviderMock(): IssueProvider {
    return {
        comment: () => Promise.resolve(),
        setArtifacts: () => Promise.resolve(),
        getKey: () => Promise.resolve('SOME-12321')
    };
}

export function getGraphMock(): Partial<TkitGraph> {
    const mock = {
        addStep: ({name}) => name
    };

    sinon.spy(mock, 'addStep');

    return mock;
}

export function getSandboxMock() {
    return {
        getReleaseResources: sinon.stub(),
        getTaskResources: sinon.stub()
    };
}

export function getYappyMock() {
    return {
        createBeta: sinon.stub().resolves('yappy-beta-x123'),
        updateOrCreateBeta: sinon.stub().resolves('yappy-beta-x123'),
        getBetaStatus: sinon.stub().resolves('CONSISTENT')
    };
}

export function getResourceMock({
    id = String(parseInt(String(Math.random() * 100000), 10)),
    type = 'TEST_RESOURCE_TYPE',
    attributes
}: {id?: string; type?: SandboxResource['type']; attributes?: SandboxResource['attributes']}): SandboxResource {
    return {
        id,
        type,
        attributes: attributes || null,
        size: 500,
        url: `https://sandbox/api/url/${id}`,
        http: {
            proxy: `https://sandbox/proxy/url/${id}`
        },
        description: `test resource of ${type}`,
        file_name: 'path/to/resource',
        skynet_id: `rbtorrent:000000000${id}`,
        task: {
            status: 'SUCCESS',
            url: `https://sandbox/task/task-${id}`,
            id: `task-${id}`
        }
    };
}

export function getStartrekIssueMock({
    status = 'Deploying',
    appVersion = undefined
}: {status?: string; appVersion?: string} = {}) {
    return {
        'self': 'https://st-api.yandex-team.ru/v2/issues/HOME-00000',
        'id': 'fakeid',
        'key': 'HOME-00000',
        'appVersion': appVersion,
        'version': 113,
        'components': [
        ],
        // eslint-disable-next-line max-len
        'description': "// Место для записей человеком\n==== Ссылки\n\n((https://error.yandex-team.ru/projects/morda/projectDashboard?filter=environment%20==%20pre_production%20and%20level%20!=%20info Error booster)) ((https://sandbox.yandex-team.ru/tasks/?type=NANNY_RELEASE_MANY_RESOURCES&all_tags=true&tags=morda,2022-02-16-0,unstable Nanny Deploy)) ((https://teamcity.yandex-team.ru/buildConfiguration/PortalAkaMordaProjects_PortalMordaXenial_PortalMordaAutotestingRc Гермиона)) ((https://sandbox.yandex-team.ru/task/1217304003 Сборка в сандбоксе))\n\n==== Ресурсы\n\n- ((https://sandbox.yandex-team.ru/resources?type=PORTAL_MORDA_FRONT_TARBALL&attrs=%7B%22version%22%3A%222022-02-15-0%22%7D PORTAL_MORDA_FRONT_TARBALL=2022-02-15-0))\n- ((https://sandbox.yandex-team.ru/resources?type=PORTAL_MORDA_TMPL_SKINS_TARBALL&attrs=%7B%22version%22%3A%222022-02-15-0%22%7D PORTAL_MORDA_TMPL_SKINS_TARBALL=2022-02-15-0))\n- ((https://sandbox.yandex-team.ru/resources?type=PORTAL_MORDA_TMPL_TARBALL&attrs=%7B%22version%22%3A%222022-02-16-0%22%7D PORTAL_MORDA_TMPL_TARBALL=2022-02-16-0))\n- ((https://proxy.sandbox.yandex-team.ru/2796034440/log?force_text_mode=1 s3 tmpl))\n\n==== Дежурные\n\n- **Backend & Infra**: dkhlynin@\n- **Фронтенд**: ivanovsky-v@\n- **Тестирование**: askordet@\n\n==== Задачи\n\n- ((https://st.yandex-team.ru/HOME-70624 HOME-70624: ☂ Эксперимент с использованием аппхостового reqid'а))\n- ((https://st.yandex-team.ru/HOME-76068 HOME-76068: [touch] Поддержать единую схему блока Новостей в верстке))\n- ((https://st.yandex-team.ru/HOME-76524 HOME-76524: [ desktop ] Раскатить редизайн десктопной морды во фронтенде))\n- ((https://st.yandex-team.ru/HOME-76652 HOME-76652: [perl init] Доделки по переезду блока Новостей в Авокадо))\n- ((https://st.yandex-team.ru/HOME-76938 HOME-76938: Видео баннер на таче v2))\n- ((https://st.yandex-team.ru/HOME-77310 HOME-77310: Починить бету))\n- ((https://st.yandex-team.ru/HOME-77434 HOME-77434: [touch] Верстка страницы некорректна после авторизации пользователя))\n\n==== Коммиты\n\n<{Развернуть\n- ⦿ ((/mock/1 HOME-12345: test))\n- ⦿ ((/mock/2 HOME-12346: test (2)))}>\n\n==== Примечания разработки\n\n\n\n==== Особенности релиза\n\n\n\n==== Как отключить фичу при сбое\n\n\n\n==== Что может пойти не так\n\n\n\n==== Сделать после релиза\n\n\n\n==== Не вся информация извлечена\n\n- В описании этих задач не нашлось нужных заголовков. Возможно их там нет, либо описание размечено неверно. Некоторые инструкции из этих задач могли быть не скопированы в это описание.\n- ((https://st.yandex-team.ru/HOME-70624 HOME-70624: ☂ Эксперимент с использованием аппхостового reqid'а))\n- ((https://st.yandex-team.ru/HOME-76068 HOME-76068: [touch] Поддержать единую схему блока Новостей в верстке))\n- ((https://st.yandex-team.ru/HOME-76524 HOME-76524: [ desktop ] Раскатить редизайн десктопной морды во фронтенде))\n- ((https://st.yandex-team.ru/HOME-76652 HOME-76652: [perl init] Доделки по переезду блока Новостей в Авокадо))\n- ((https://st.yandex-team.ru/HOME-76938 HOME-76938: Видео баннер на таче v2))\n- ((https://st.yandex-team.ru/HOME-77310 HOME-77310: Починить бету))\n- ((https://st.yandex-team.ru/HOME-77434 HOME-77434: [touch] Верстка страницы некорректна после авторизации пользователя))\n",

        'type': {
            'key': 'release',
            'display': 'Release'
        },
        'createdAt': '2022-02-15T15:18:19.743+0000',
        'summary': 'Релиз morda: 2022-02-16-0',
        'priority': {
            'key': 'normal',
            'display': 'Normal'
        },
        'tags': [
            'urelease:morda'
        ],
        'followers': [
        ],
        'queue': {
            'key': 'HOME',
            'display': 'Морда'
        },
        'status': {
            'key': status,
            'display': status
        },
        'favorite': false
    };
}
