import nock from 'nock';

import {STAFF_API, StaffClient} from './staff-client';
import {STAFF_FIELDS_DEFAULT} from './types';

const LOGIN = 'pigeon';
const USER_TICKET = 'userTicket';
const SERVICE_TICKET = 'serviceTicket';

describe('package "staff-provider"', () => {
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

    it('should return only specified fields', async () => {
        const staffClient = new StaffClient();

        nock(STAFF_API)
            .get('/persons')
            .query({
                _one: 1,
                login: LOGIN,
                _fields: STAFF_FIELDS_DEFAULT.join(',')
            })
            .reply(200, {
                name: 1,
                images: 2,
                environment: '33',
                language: '44',
                foo: 'bar',
                bar: 'foo'
            });

        const data = await staffClient.getPerson({
            userTicket: '',
            serviceTicket: '',
            login: LOGIN
        });

        expect(data).toEqual({
            name: 1,
            images: 2,
            environment: '33',
            language: '44'
        });
    });

    it('should contain in request specified headers', async () => {
        const staffClient = new StaffClient();

        nock(STAFF_API, {
            reqheaders: {
                'x-ya-service-ticket': SERVICE_TICKET,
                'x-ya-user-ticket': USER_TICKET
            }
        })
            .get('/persons')
            .query({_one: 1, login: LOGIN, _fields: STAFF_FIELDS_DEFAULT.join(',')})
            .reply(200, {
                name: 1,
                images: 2,
                environment: '33',
                language: '44'
            });

        const data = await staffClient.getPerson({
            userTicket: USER_TICKET,
            serviceTicket: SERVICE_TICKET,
            login: LOGIN
        });

        expect(data).toEqual({
            name: 1,
            images: 2,
            environment: '33',
            language: '44'
        });
    });

    it('should add "_fields" in query if it specified', async () => {
        const staffClient = new StaffClient();

        nock(STAFF_API).get('/persons').query({_one: 1, login: LOGIN, _fields: 'foo,bar'}).reply(200, {
            name: 1,
            images: 2,
            environment: '33',
            language: '44'
        });

        const data = await staffClient.getPerson({
            userTicket: '',
            serviceTicket: '',
            login: LOGIN,
            fields: ['foo', 'bar']
        });

        expect(data).toEqual({
            name: 1,
            images: 2,
            environment: '33',
            language: '44'
        });
    });
});
