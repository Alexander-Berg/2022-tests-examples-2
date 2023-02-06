const {parseStr} = require('../util');

describe('util', function () {
    describe('parseStr', function () {
        it('возвращает пустой массив, если строка не матчится', function () {
            parseStr('', /(\w)/).should.be.an('array');
            parseStr('qweqwe', /(\w)/).should.be.an('array');
            parseStr('111:1111', /(x)/).should.be.an('array');
            parseStr('file:111:1111', /(x)/).should.be.an('array');
        });
        it('находит несколько экспериментов в одной строке', function () {
            parseStr('file:123: x(qwe) x(rty)', /(x)\((\w+)\)/)
                .should.deep.equal([
                    ['qwe', 'file:123'],
                    ['rty', 'file:123']
                ]);
        });
    });
});
