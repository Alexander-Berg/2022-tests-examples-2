/* eslint dot-notation: 0, no-unused-expressions: 0 */
describe('home.checkObjProp', function() {
    it('работает как задумано', function() {
        home.checkObjProp({a: 1}, 'a').should.be.true;
        home.checkObjProp({a: {a: 1}}, 'a.a').should.be.true;
        home.checkObjProp({a: {a: {a: 1}}}, 'a.a.a').should.be.true;
        home.checkObjProp({}, 'a.a.b').should.be.false;
        home.checkObjProp({a: {a: {a: 0}}}, 'a.a.a').should.be.false;
        home.checkObjProp({a: {a: {a: '0'}}}, 'a.a.a').should.be.false;
        home.checkObjProp({a: {a: {a: undefined}}}, 'a.a.a').should.be.false;
        home.checkObjProp({a: {a: {a: 1}}}, 'a.a.a.a.a.a.a').should.be.false;
        home.checkObjProp({a: {'': 1}}, 'a.').should.be.true;
    });
});

describe('home.convertQueryToJson', function() {
    it('работает как задумано', function() {
        home.convertQueryToJson('?param1=123').should.deep.equal({param1: '123'});
        home.convertQueryToJson('?param1=123&param2=value').should.deep.equal({param1: '123', param2: 'value'});
    });

    it('преобразует параметр без значения', function() {
        home.convertQueryToJson('?param1=&param2=value').should.deep.equal({param1: '', param2: 'value'});
    });

    it('преобразует строку без "?"', function() {
        home.convertQueryToJson('param1=123&param2=value').should.deep.equal({param1: '123', param2: 'value'});
    });
});
