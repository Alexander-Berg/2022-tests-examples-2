describe('i-counter-code', function () {
    var expect = chai.expect,
        block = BN('i-counter-code');

    describe('counter', function () {
        describe('script filename', function () {
            it('watch.js', function () {
                var name;

                name = block._getCounterFileName({});
                expect(name).to.equal('watch');

                name = block._getCounterFileName({}, false);
                expect(name).to.equal('watch');

                name = block._getCounterFileName({webvisorBeta: false}, false);
                expect(name).to.equal('watch');
            });

            it('watch_beta.js', function () {
                var name;

                name = block._getCounterFileName({}, true);
                expect(name).to.equal('watch_beta');

                name = block._getCounterFileName({webvisorBeta: false}, true);
                expect(name).to.equal('watch_beta');
            });

            it('tag.js', function () {
                var name;

                name = block._getCounterFileName({webvisorBeta: true});
                expect(name).to.equal('tag');

                name = block._getCounterFileName({webvisorBeta: true}, true);
                expect(name).to.equal('tag');
            });
        });

        describe('constructor name', function () {
            it('Ya.Metrika', function () {
                var name;

                name = block._getCounterClassName({});
                expect(name).to.equal('Ya.Metrika');

                name = block._getCounterClassName({webvisorBeta: false});
                expect(name).to.equal('Ya.Metrika');
            });

            it('Ya.Metrika2', function () {
                var name;

                name = block._getCounterClassName({webvisorBeta: true});
                expect(name).to.equal('Ya.Metrika2');
            });
        });

        describe('callbacks variable name', function () {
            it('yandex_metrika_callbacks', function () {
                var name;

                name = block.getCallbacksVariableName({});
                expect(name).to.equal('yandex_metrika_callbacks');

                name = block.getCallbacksVariableName({webvisorBeta: false});
                expect(name).to.equal('yandex_metrika_callbacks');
            });

            it('yandex_metrika_callbacks2', function () {
                var name;

                name = block.getCallbacksVariableName({webvisorBeta: true});
                expect(name).to.equal('yandex_metrika_callbacks2');
            });
        });
    });

    // todo informer

});
