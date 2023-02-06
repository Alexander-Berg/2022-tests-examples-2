import test from 'ava';
import render from '../src/ssr.jsx';

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
    return render('index', '/', appData)
        .then(({html}) => {
            t.true(html.indexOf('<script nonce="foobar">') > -1);
        });
});
