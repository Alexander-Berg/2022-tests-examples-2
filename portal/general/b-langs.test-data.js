/* eslint-env es6 */

exports.simple = (execView) => '<div style="padding: 100px;">' + execView('BLangs', {}, {
    Locale: 'be',
    MordaZone: 'ru',
    LanguageChooserInFooter: [
        {
            'locale': 'ru',
            'selected': '',
            'href': 'https://yandex.ru/?lang=ru&sk=y67e14076e73fbabd370225ab97e32055',
            'lang': 'ru'
        },
        {
            'locale': 'be',
            'selected': '1',
            'href': 'https://yandex.ru/?lang=be&sk=y67e14076e73fbabd370225ab97e32055',
            'lang': 'by'
        }
    ],
    JSON: {
        common: {
            language: 'by'
        }
    }
}) + '</div>';
