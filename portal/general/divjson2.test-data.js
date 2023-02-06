const fs = require('fs');
const path = require('path');

let tests = {};

let mockImages = new Map();
// Заменяем внешние файлы заинлайненными
mockImages.set('https://alicekit.s3.yandex.net/images_for_divs/chess.png', 'local://chess.png');
mockImages.set('https://alicekit.s3.yandex.net/images_for_divs/chess_transparent.png', 'local://chess_transparent.png');
mockImages.set('https://pages.github.yandex-team.ru/7seas/work/specs/pp_bridges_v2/assets/wave_1col.4.png', 'local://wave_1col.4.png');
mockImages.set('https://yastatic.net/s3/home/yandex-app/services_div/general/2menu_points.2.png', 'local://2menu_points.2.png');
mockImages.set('https://api.yastatic.net/morda-logo/i/yandex-app/district/images_day.1.png', 'local://images_day.1.png');
mockImages.set('https://i.imgur.com/CPmGi24.png', 'local://CPmGi24.png');
mockImages.set('https://yastatic.net/s3/home/yandex-app/services_div/general/menu_points.3.png', 'local://menu_points.3.png');
mockImages.set('https://i.imgur.com/qNJQKU8.png', 'local://menu_points.3.png');
// Заменяем сложную картинку на заинлайненную попроще
mockImages.set('https://alicekit.s3.yandex.net/images_for_divs/nature.jpg', '[% mockSvg %]');
mockImages.set('https://avatars.mds.yandex.net/get-yapic/40841/520495100-1548277370/islands-200', '[% mockSvg %]');
mockImages.set(/https:\/\/i\.ibb\.co\/[^"]+/g, '[% mockSvg %]');
mockImages.set('https://imgur.com/hcD8ABF.png', '[% mockSvg %]');
mockImages.set('http://imgur.com/7y1xr5j.png', '[% mockSvg %]');
mockImages.set('https://c.tcdn.co/62d/c81/62dc816e-5b24-11e6-a5c8-040157cdaf01/channel256.png', '[% mockSvg %]');
mockImages.set('https://avatars.mds.yandex.net/get-pdb/1340633/88a085e7-7254-43ff-805a-660b96f0e6ce/s1200?webp=false', '[% mockSvg %]');
// eslint-disable-next-line max-len
mockImages.set(/https:\/\/avatars\.mds\.yandex\.net\/get-bass\/[^"]+/g, '[% mockSvg %]');
// Заменяем несуществующую картинку на другую несуществующую
mockImages.set(/"image_url":"https:\/\/yandex\.ru"/g, '"image_url":"/empty"');

function encodeRE (val) {
    return val.replace(/[-[\]/{}()*+?.\\^$|]/g, '\\$&');
}

let resultMockImages = new Map();
for (let [key, val] of mockImages.entries()) {
    if (typeof key === 'string') {
        key = new RegExp(encodeRE(key), 'g');
    }
    if (val.startsWith('local://')) {
        val = `data:image/png;base64,${fs.readFileSync(__dirname + '/test-images/' + val.replace('local://', '')).toString('base64')}`;
    }
    resultMockImages.set(key, val);
}

read('mocks/crossplatform', 'crossplatform/', true);
read('mocks/custom', 'custom/', false);

function read (dir, prefix, isCrossplatform) {
    function append (dir, prefix) {
        const items = fs.readdirSync(path.join(__dirname, dir));

        for (const item of items) {
            if (item.endsWith('.json')) {
                tests[prefix + item.replace('.json', '')] = isCrossplatform;
            } else {
                append(path.join(dir, item), prefix + item + '/');
            }
        }
    }

    append(dir, prefix);
}

for (let name in tests) {
    exports[name] = (execView, {home}) => {
        let json;

        if (tests[name]) {
            let templates = {};
            let templatesPath = path.resolve(__dirname, `./mocks/${name.replace(/\/[^/]+$/, '/templates.json')}`);

            if (fs.existsSync(templatesPath)) {
                templates = require(templatesPath);
            }
            json = {
                templates,
                card: require(`./mocks/${name}.json`)
            };
        } else {
            json = require(`./mocks/${name}.json`);
        }

        let jsonStr = JSON.stringify(json);

        for (const [key, val] of resultMockImages.entries()) {
            jsonStr = jsonStr.replace(key, val);
        }
        json = JSON.parse(jsonStr);

        let origError = home.error;
        home.error = function (opts) {
            if (opts && opts.level === 'warn' || opts.message === 'Too many constrained items') {
                return;
            }
            return origError(opts);
        };

        try {
            return `<style>
                body {
                    margin: 0;
                }
            </style><div class="wrapper" style="width:360px;font-family: 'YS Text', sans-serif;font-size: 20px;min-height:1px;">
            ${execView('Divjson2', {
        layoutName: 'test',
        json
    }, {
        LiveCartridge: 1,
        setCounter: () => {
        }
    })}
                </div><script>
                $(function () {
                    $('.imageloader').toArray().forEach(function (block){
                        $(block).bem('imageloader').setMod('visible', 'yes');
                    });
                });
            </script>`;
        } finally {
            home.error = origError;
        }
    };
}
