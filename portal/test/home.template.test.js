describe('home.template', function() {
    var generatedClsReq = {
        antiadb_desktop: 1,
        clsGen: true
    };

    generatedClsReq.cls = home.cls(generatedClsReq);

    beforeEach(function () {
        home.cls.setMap(null);
    });

    describe('prefix', function () {
        function wrap(func, str) {
            return function (data, req) {
                return func(data, req || data, str);
            };
        }
        describe('prefix bem classname', function() {
            var data = {mods: {e: 't'}, mix: 'qq', smth: {mods: {w: 'r'}}},
                testClassname = wrap(home.parseRules.bem, 'b-block.class'),
                testClassname2 = wrap(home.parseRules.bem, 'smth.b-block2.class');

            it('понимает название класса', function() {
                testClassname(data).should.equal('b-block qq b-block_e_t');
            });

            it('понимает указание источника свойств', function() {
                testClassname2(data).should.equal('b-block2 b-block2_w_r');
            });
        });

        describe('prefix bem js', function() {
            var data = {js: {w: 1}, smth: {q: 3}},
                testJs = wrap(home.parseRules.bem, 'js'),
                testJs2 = wrap(home.parseRules.bem, 'smth.js');

            it('работает как ожидается', function() {
                testJs(data).should.equal('{&quot;w&quot;:1}');
            });

            it('понимает указание источника свойств', function() {
                testJs2(data).should.equal('{&quot;q&quot;:3}');
            });
        });

        describe('prefix bem attrs', function() {
            var data = {attrs: {title: 'w', src: 'sdfsdf.png'}, smth: {name: 'q', value: '1'}},
                testAttrs = wrap(home.parseRules.bem, 'attrs'),
                testAttrs2 = wrap(home.parseRules.bem, 'smth.attrs');

            it('работает как ожидается', function() {
                testAttrs(data).should.equal(' title="w" src="sdfsdf.png"');
            });

            it('понимает указание источника свойств', function() {
                testAttrs2(data).should.equal(' name="q" value="1"');
            });
        });

        describe('prefix bem classname with generated classes and empty map', function () {
            var data = {mods: {e: 't'}, mix: 'qq', smth: {mods: {w: 'r'}}},
                testClassname = wrap(home.parseRules.bem, 'b-block.class'),
                testClassname2 = wrap(home.parseRules.bem, 'smth.b-block2.class');

            it('понимает название класса', function() {
                testClassname(data, generatedClsReq).should.equal('b-block qq b-block_e_t');
            });

            it('понимает указание источника свойств', function() {
                testClassname2(data, generatedClsReq).should.equal('b-block2 b-block2_w_r');
            });
        });

        describe('prefix bem classname with generated classes and fullfilled map', function () {
            var data = {mods: {e: 't'}, mix: 'qq', smth: {mods: {w: 'r'}}},
                testClassname = wrap(home.parseRules.bem, 'b-block.class'),
                testClassname2 = wrap(home.parseRules.bem, 'smth.b-block2.class');

            it('должно пытаться использовать сгенеренные классы', function () {
                home.cls.setMap({
                    list: ['b-block'],
                    map: {
                        'b-block': 'bb'
                    },
                    blocks: []
                });

                generatedClsReq.cls.generated.should.equal(true);
            });

            it('понимает название класса', function() {
                home.cls.setMap({
                    list: ['b-block'],
                    map: {
                        'b-block': 'bb'
                    },
                    blocks: []
                });

                testClassname(data, generatedClsReq).should.equal('bb qq b-block_e_t');
            });

            it('понимает название класса 2', function() {
                home.cls.setMap({
                    list: [],
                    map: {
                        'b-block': 'bb'
                    },
                    blocks: ['b-block']
                });

                testClassname(data, generatedClsReq).should.equal('bb qq bb_e_t');
            });

            it('понимает указание источника свойств', function() {
                home.cls.setMap({
                    list: [
                        'b-block',
                        'b-block2_w_r'
                    ],
                    map: {
                        'b-block': 'bb',
                        'b-block2': 'bb2',
                        'w': 'w',
                        'r': 'r'
                    },
                    blocks: []
                });

                testClassname2(data, generatedClsReq).should.equal('b-block2 bb2_w_r');
            });

            it('понимает название класса с заменённым модификатором', function() {
                home.cls.setMap({
                    list: [
                        'b-block',
                        'b-block_e_t'
                    ],
                    map: {
                        'b-block': 'bb',
                        'e': 'e',
                        't': 't'
                    },
                    blocks: []
                });

                testClassname(data, generatedClsReq).should.equal('bb qq bb_e_t');
            });
        });

        describe('prefix cls', function () {
            var testClassname = wrap(home.parseRules.cls, 'some-block'),
                testClassname2 = wrap(home.parseRules.cls, 'some__other');

            it('should work without cls', function () {
                testClassname({}).should.equal('some-block');
                testClassname2({}).should.equal('some__other');
            });

            it('should replace classes', function () {
                home.cls.setMap({
                    list: [
                        'some-block',
                        'some__other'
                    ],
                    map: {
                        'some-block': 'sb',
                        'some': 'se',
                        'other': 'or'
                    },
                    blocks: []
                });

                testClassname({}, generatedClsReq).should.equal('sb');
                testClassname2({}, generatedClsReq).should.equal('se__or');
            });

            it('should replace classes', function () {
                home.cls.setMap({
                    list: [
                        'some-block'
                    ],
                    map: {
                        'some-block': 'sb',
                        'some': 'se',
                        'other': 'or'
                    },
                    blocks: [
                        'some'
                    ]
                });

                testClassname({}, generatedClsReq).should.equal('sb');
                testClassname2({}, generatedClsReq).should.equal('se__other');
            });
        });
    });
});
