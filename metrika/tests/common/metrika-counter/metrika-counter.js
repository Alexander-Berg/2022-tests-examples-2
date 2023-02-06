describe('metrika-counter watch.js', function () {
    var expect = chai.expect,
        block,
        elem,
        blockName = 'metrika-counter';

    beforeEach(function (done) {
        BEM.blocks['i-content'].html({
            block: blockName,
            counterId: 3
        }).then(function (html) {
            elem = $(html).appendTo('body');
            BEM.DOM.init($(elem), function () {
                block = elem.bem(blockName);
                done();
            });
        }).fail(function (err) {
            done(err);
        });
    });

    afterEach(function () {
        BEM.DOM.destruct(elem);
    });

    it('params', function () {
        expect(block.params.callbacksVariableName).to.equal('yandex_metrika_callbacks');
    });
});

describe('metrika-counter tag.js', function () {
    var expect = chai.expect,
        block,
        elem,
        blockName = 'metrika-counter';

    beforeEach(function (done) {
        BEM.blocks['i-content'].html({
            block: blockName,
            counterId: 3,
            counterOptions: {
                webvisorBeta: true,
                async: true
            }
        }).then(function (html) {
            elem = $(html).appendTo('body');
            BEM.DOM.init($(elem), function () {
                block = elem.bem(blockName);
                done();
            });
        }).fail(function (err) {
            done(err);
        });
    });

    afterEach(function () {
        BEM.DOM.destruct(elem);
    });

    it('params', function () {
        expect(block.params.callbacksVariableName).to.equal('yandex_metrika_callbacks2');
    });
});
