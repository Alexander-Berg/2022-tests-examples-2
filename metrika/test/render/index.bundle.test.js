import { createElement } from 'react';
import test from 'ava';
import App from '../../src/components/app';
import render from '../../src/ssr.jsx';

const appData = {
    lang: 'ru',
    i18n: {
        ru: {
            title: 'Реактив-стаб'
        },
        en: {
            title: 'Reactive-Stub'
        }
    },
    nonce: 'foobar',
    staticHost: './static',
    bundle: 'index'
};

test('server-side rendering', t => {
    const template = /<div\sid="mount"><div\sclass="app"\sdata-reactroot="">.+?<\/div><\/div>/;

    return render({ bundleName: 'index', location: '/', appData })
        .then(({ html }) => {
            t.true(template.test(html));
        });
});

test('client rendering', t => {
    const app = createElement(App, { appData }, null);

    t.truthy(app);
});
