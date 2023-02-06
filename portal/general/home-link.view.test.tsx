import { execView } from '@lib/views/execView';
import { toElement } from '@lib/views/toElement';
import { HomeLink } from '@block/home-link/home-link.view';

describe('home-link', () => {
    test('renders link', () => {
        // <a>
        expect(execView(HomeLink, {
            href: '//ya.ru',
            content: 'abc'
        })).toMatchSnapshot();

        // <span>
        expect(execView(HomeLink, {
            content: 'abc'
        })).toMatchSnapshot();
    });

    test('renders with props', () => {
        expect(execView(HomeLink, {
            href: '//ya.ru',
            content: 'abc',
            mods: {
                theme: 'super'
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
        expect(toElement(execView(HomeLink, {
            href: '//ya.ru',
            content: 'abc',
            target: '_blank'
        })).getAttribute('rel')).toEqual('noopener');
    });
});
