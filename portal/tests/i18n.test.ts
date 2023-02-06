/* eslint-env node, mocha */
import * as assert from 'assert';
import {I18n, Dict} from '../i18n';

describe('i18n', () => {
    it('should handle plural forms', () => {
        const dict: Dict = {
            'pp.znatoki.more_answers': ['Еще %1 ответ', 'Еще %1 ответа', 'Еще %1 ответов', '1 ответ']
        };
        const i18n = new I18n(dict);

        assert.equal(i18n.translate('pp.znatoki.more_answers', 0), '1 ответ');
        assert.equal(i18n.translate('pp.znatoki.more_answers', 1), 'Еще 1 ответ');
        assert.equal(i18n.translate('pp.znatoki.more_answers', 23), 'Еще 23 ответа');
        assert.equal(i18n.translate('pp.znatoki.more_answers', 44), 'Еще 44 ответа');
        assert.equal(i18n.translate('pp.znatoki.more_answers', 46), 'Еще 46 ответов');
        assert.equal(i18n.translate('pp.znatoki.more_answers', 113), 'Еще 113 ответов');
        assert.equal(i18n.translate('pp.znatoki.more_answers', 123), 'Еще 123 ответа');
    });

    it('should substitute placeholders with arguments', () => {
        const dict: Dict = {
            'test1': '%1 один %2 два %3 три'
        };
        const i18n = new I18n(dict);
        assert.equal(i18n.translate('test1', 1, 2, '3'), '1 один 2 два 3 три');
        assert.equal(i18n.translate('test1', 1), '1 один %2 два %3 три');
        assert.equal(i18n.translate('test1', 1, 2, 3, 4), '1 один 2 два 3 три');
    });
});