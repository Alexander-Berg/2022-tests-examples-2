import { execView } from '@lib/views/execView';

// todo move to imports

describe('content-tabs', function() {
    it('renders tabs', function() {
        expect(execView('ContentTabs', {
            items: [
                {
                    relId: '610367',
                    title: {
                        content: 'Новости',
                        href: 'http://ya.ru'
                    },
                    active: true,
                    content: 'Новости'
                },
                {
                    relId: '887133',
                    title: {
                        content: 'в Москве',
                        href: 'http://ya.ru'
                    },
                    active: false,
                    content: 'Новости Москвы'
                }
            ]
        })).toMatchSnapshot();
    });
});
