import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-ignore
import { Logo } from './logo.view';

describe('logo', function() {
    it('renders default logo', function() {
        expect(execView(Logo, mockReq())).toMatchSnapshot();
    });

    it('renders default logo instead of one from export', function() {
        let mockObj = mockReq({}, {
            JSON: {},
            Logo: {
                voffset: '-8',
                href: 'http://yandex.ru/yandsearch?text=%D0%94%D0%B5%D0%BD%D1%8C+%D0%9F%D0%BE%D0%B1%D0%B5%D0%B4%D1%8B',
                url: 'pobeda',
                title: 'С Днём Победы!',
                show: 1,
                counter: 'test'
            }
        });
        expect(execView(Logo, mockObj)).toMatchSnapshot();
    });
});
