import { execView } from '@lib/views/execView';
import { toElement } from '@lib/views/toElement';
import { HomeLink2 } from '@block/home-link2/home-link2.view';

describe('home-link2', () => {
    test('renders link', () => {
        // <a>
        expect(execView(HomeLink2, {
            href: '//ya.ru',
            content: 'abc'
        })).toMatchSnapshot();

        // <span>
        expect(execView(HomeLink2, {
            content: 'abc'
        })).toMatchSnapshot();
    });

    test('renders with props', () => {
        expect(execView(HomeLink2, {
            href: '//ya.ru',
            content: 'abc',
            mods: {
                color: 'inherit'
            },
            title: 'Tooltip',
            role: 'Role',
            tabindex: '2',
            target: '_self',
            attrs: {
                a: 'b'
            },
            stat: ' data-stat',
            js: {
                some: { c: 4 }
            },
            inlineIcon: 'icon'
        })).toMatchSnapshot();
    });

    test('renders with rel=noopener', () => {
        expect(toElement(execView(HomeLink2, {
            href: '//ya.ru',
            content: 'abc',
            target: '_blank'
        })).getAttribute('rel')).toEqual('noopener');
    });
});
