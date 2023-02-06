const { transformInlineResources } = require('./inline-resources-transformer');
const { parse } = require('@babel/parser');
const generate = require('@babel/generator').default;

const chai = require('chai');
const chaiJestSnapshot = require('chai-jest-snapshot');

chai.use(chaiJestSnapshot);

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});

describe('transform inline resources', () => {
    it('should transform home.fileContents.get(...)(path) calls', () => {
        const path = 'white/blocks/index/logo/logo.view.js';
        const src = `views('logo__image', function (data, req, execView) {
                        if (req.Logo && req.Logo.url && execView('logo__custom')) {
                            data.fallback = home.fileContents.get('uglify')('white/blocks/index/logo/logo.fallback.js');
                            return execView('logo__img', data);
                        } else {
                        return execView('logo__div', data);
                        }
                    });`;
        const ast = transformInlineResources(parse(src), path);
        const result = generate(ast).code;
        chai.expect(result).to.matchSnapshot();
    });

    it('should transform req.resources.inline(src, type, ...) calls', () => {
        const path = 'blocks/common/rum-error/rum-error.view.js';
        const src = `rumDependencies.forEach(function(fileName) {
                        const extension = isDev ? '.js' : '.min.js';
                        req.resources.inline('../node_modules/@yandex-int/error-counter/dist/filters.min.js', 'js', 'head');
                     });`;
        const ast = transformInlineResources(parse(src), path);
        const result = generate(ast).code;
        chai.expect(result).to.matchSnapshot();
    });

    it('should transform home.fileContents.get(...)(path) indirect calls', () => {
        const path = 'touch/blocks/touch/mlogo/mlogo.view.js';
        const src = `var logos = home.fileContents.get('backgroundUrl');
                     views('mlogo__default-png', function () {
                        return logos('touch/blocks/touch/mlogo/mlogo.assets/mlogo.png');
                     });
        
                     views('mlogo__default-svg', function (suffix) {
                        return logos('touch/blocks/touch/mlogo/mlogo.assets/mlogo.svg');
                     });`;

        const ast = transformInlineResources(parse(src), path);
        const result = generate(ast).code;
        chai.expect(result).to.matchSnapshot();
    });
});
