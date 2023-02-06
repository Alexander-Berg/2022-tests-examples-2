import {Divjson2__filter} from '@block/divjson2/divjson2.view';
import {Divjson2Block} from '@block/divjson2-block/divjson2-block.view';

views('divjson2-test-block', function (data, req, execView) {
    if (!execView(Divjson2__filter)) {
        return;
    }

    return execView(Divjson2Block, {
        layoutName: 'test',
        test: true,
        api: req.Getargshash.add_div2,
        title: 'Тестовый блок',
        cardWidth: 116
    });
});
