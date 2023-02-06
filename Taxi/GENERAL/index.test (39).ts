import nock from 'nock';
import {URL} from 'url';

import {ABC_API_URL, SERVICES_MEMBERS_LOCATION} from '.';
import {AbcProvider} from './abc-provider';

const SERVICES_MEMBERS_REPLY = {
    next: null,
    previous: null,
    results: [
        {
            id: 662696,
            person: {id: 139984, login: 'testUser', uid: '1120000000262642'},
            service: {id: 34126, slug: 'lavkajstoolbox'},
            role: {id: 8, scope: {slug: 'development'}, code: 'developer'},
            department_member: null
        },
        {
            id: 675296,
            person: {id: 139984, login: 'testUser', uid: '1120000000262642'},
            service: {id: 34126, slug: 'lavkajstoolbox'},
            role: {id: 1260, scope: {slug: 'robots_management'}, code: 'robots_manager'},
            department_member: null
        },
        {
            id: 681022,
            person: {id: 139984, login: 'testUser', uid: '1120000000262642'},
            service: {id: 34126, slug: 'lavkajstoolbox'},
            role: {id: 1097, scope: {slug: 'devops'}, code: 'devops'},
            department_member: null
        }
    ]
};

describe('package "abc"', () => {
    beforeAll(async () => {
        nock.disableNetConnect();
        nock.enableNetConnect(/localhost/);
    });

    afterAll(async () => {
        nock.enableNetConnect();
    });

    afterEach(async () => {
        nock.cleanAll();
    });

    it('should handle "getRolesByLogin" method', async () => {
        const provider = new AbcProvider({getServiceTicket});
        const url = new URL([ABC_API_URL, SERVICES_MEMBERS_LOCATION].join('/'));

        nock(url.origin)
            .get(url.pathname)
            .query({person__login: 'testUser', service__slug__in: 'foo,bar'})
            .reply(200, SERVICES_MEMBERS_REPLY);

        const roles = await provider.getRolesByLogin({
            userTicket: 'ticket',
            login: 'testUser',
            serviceSlugs: ['foo', 'bar']
        });

        expect(roles).toEqual([
            {
                department_member: null,
                id: 662696,
                person: {id: 139984, login: 'testUser', uid: '1120000000262642'},
                role: {code: 'developer', id: 8, scope: {slug: 'development'}},
                service: {id: 34126, slug: 'lavkajstoolbox'}
            },
            {
                department_member: null,
                id: 675296,
                person: {id: 139984, login: 'testUser', uid: '1120000000262642'},
                role: {code: 'robots_manager', id: 1260, scope: {slug: 'robots_management'}},
                service: {id: 34126, slug: 'lavkajstoolbox'}
            },
            {
                department_member: null,
                id: 681022,
                person: {id: 139984, login: 'testUser', uid: '1120000000262642'},
                role: {code: 'devops', id: 1097, scope: {slug: 'devops'}},
                service: {id: 34126, slug: 'lavkajstoolbox'}
            }
        ]);
    });

    it('should handle "hasUserRoleInService" method', async () => {
        const provider = new AbcProvider({getServiceTicket});
        const url = new URL([ABC_API_URL, SERVICES_MEMBERS_LOCATION].join('/'));

        nock(url.origin)
            .get(url.pathname)
            .query({person__login: 'testUser', service__slug__in: 'lavkajstoolbox,fooservice'})
            .reply(200, SERVICES_MEMBERS_REPLY);

        const hasUserRoleInService = await provider.hasUserRoleInService({
            userTicket: 'ticket',
            login: 'testUser',
            rolesByServices: {
                lavkajstoolbox: ['development', 'robots_management', 'devops', 'content'],
                fooservice: ['development', 'content']
            }
        });

        expect(hasUserRoleInService('lavkajstoolbox', 'development')).toBeTruthy();
        expect(hasUserRoleInService('lavkajstoolbox', 'robots_management')).toBeTruthy();
        expect(hasUserRoleInService('lavkajstoolbox', 'devops')).toBeTruthy();

        expect(hasUserRoleInService('lavkajstoolbox', 'content')).toBeFalsy();
        expect(hasUserRoleInService('fooservice', 'development')).toBeFalsy();
        expect(hasUserRoleInService('fooservice', 'content')).toBeFalsy();
    });
});

async function getServiceTicket() {
    return 'SERVICE_TICKET';
}
