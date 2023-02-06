require('should');
const cleanup = require('../lib/css-cleanup');

describe('css-cleanup', function () {
    it('не должно ломаться, если аргументы пусты', function() {
        cleanup('').should.equal('');
    });

    it('очищать правила целиком', function() {
        cleanup(
            `.test:hover {
                display: block;
            }
            
            .test:active{
                display: inline-block;
            }`,
            {selector: /:hover/}
        ).should.equal(
            '/*rule .test:hover is cleaned up*/\n' +
            '\n' +
            '.test:active {\n' +
            '  display: inline-block;\n' +
            '}'
        );
    });

    it('оставляет на месте комментарии', function() {
        cleanup(
            `.test:hover {
                display: block;
            }
            
            /* comment */
            
            .test:active{
                display: inline-block;
            }`,
            {selector: /:hover/}
        ).should.equal(
            '/*rule .test:hover is cleaned up*/\n' +
            '\n' +
            '/* comment */\n' +
            '\n' +
            '.test:active {\n' +
            '  display: inline-block;\n' +
            '}'
        );
    });

    it('очищать правила частично', function() {
        cleanup(
            `.test:hover, .test2 {
                display: block;
            }
            
            .test:active {
                display: inline-block;
            }`,
            {selector: /:hover/}
        ).should.equal(
            '/*selector .test:hover is cleaned up*/\n' +
            '\n' +
            '.test2 {\n' +
            '  display: block;\n' +
            '}\n' +
            '\n' +
            '.test:active {\n' +
            '  display: inline-block;\n' +
            '}');
    });

    it('очищать media-query', function() {
        cleanup(
            `@media (min-width: 200px) {
                .test:hover {
                    display: block;
                }
            }
            
            .test:active {
                display: inline-block;
            }`,
            {selector: /:hover/}
        ).should.equal(
            '@media (min-width: 200px) {\n' +
            '  /*rule .test:hover is cleaned up*/\n' +
            '}\n' +
            '\n' +
            '.test:active {\n' +
            '  display: inline-block;\n' +
            '}'
        );
    });
});
