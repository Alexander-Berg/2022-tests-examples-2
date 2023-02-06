import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-ignore
import { Logo } from './logo.view';

describe('logo', function() {
    it('renders simple logo', function() {
        let mockObj = mockReq({}, {
            JSON: {}
        });
        expect(execView(Logo, {}, mockObj)).toMatchSnapshot();
    });

    it('renders logo from export', function() {
        let mockObj = mockReq({}, {
            JSON: {},
            Logo: {
                voffset: '-8',
                url: 'pobeda',
                title: 'С Днём Победы!',
                show: 1,
                counter: 'test'
            }
        });
        expect(execView(Logo, {}, mockObj)).toMatchSnapshot();
    });

    it('renders logo from export with link and stat', function() {
        let mockObj = mockReq({}, {
            JSON: {
                common: {
                    language: 'ua'
                }
            },
            Logo: {
                voffset: '-8',
                hoffset: '10',
                href: 'http://yandex.ru/yandsearch?text=%D0%94%D0%B5%D0%BD%D1%8C+%D0%9F%D0%BE%D0%B1%D0%B5%D0%B4%D1%8B',
                url: 'pobeda',
                width: '100',
                height: '100',
                title: 'С Днём Победы!',
                stat: ' data-statlog="123"',
                show: 1,
                counter: 'test'
            },
        });
        expect(execView(Logo, {}, mockObj)).toMatchSnapshot();
    });
});
