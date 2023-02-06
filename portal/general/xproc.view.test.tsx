import { execView } from '@lib/views/execView';
import { HomeLink2 } from '@block/home-link2/home-link2.view';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { Xproc } from '@block/xproc/xproc.view';

// todo move to imports

describe('common xproc', function() {
    it('should render html', function() {
        expect(execView(Xproc, {
            mix: 'container',
            content: [
                {
                    mix: 'header',
                    content: 'header content'
                },
                {
                    mix: 'main',
                    content: [
                        {
                            mix: 'title',
                            content: 'hello world'
                        },
                        {
                            name: HomeLink2,
                            href: 'http://www.yandex.ru',
                            content: 'go to this link'
                        }
                    ]
                },
                {
                    mix: 'second',
                    content: {
                        name: HomeLink2,
                        href: 'http://www.google.com',
                        content: 'second link'
                    }
                },
                {
                    mix: 'footer',
                    content: 'footer content'
                }
            ]
        })).toMatchSnapshot();
    });
});
