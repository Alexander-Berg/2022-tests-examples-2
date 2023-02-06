import {Divjson2__filter} from '@block/divjson2/divjson2.view';
import {Input} from '@block/input/input.view';
import {Script, Style} from '@block/common/common.view';
import {Divjson2Block} from '@block/divjson2-block/divjson2-block.view';

import testScript from './divjson2-test-block-inline?inline';
import testStyle from './divjson2-test-block-inline.css?inline';

(function () {
    views('divjson2-test-block__check', function (data, req, execView) {
        return execView(Divjson2__filter);
    });

    views('divjson2-test-block__server-side', function (data, req, execView) {
        return execView(Input, {
            mix: 'divjson2-block__test-input',
            mods: {
                type: 'textarea',
                theme: 'normal',
                size: 's'
            }
        }) + execView(Script, {
            content: testScript
        }) + execView(Style, {
            content: testStyle
        }) + execView(Divjson2Block, {
            layoutName: 'test',
            test: true,
            api: req.Getargshash.add_div2,
            title: 'Тестовый блок',
            cardWidth: 120
        });
    });
})();
