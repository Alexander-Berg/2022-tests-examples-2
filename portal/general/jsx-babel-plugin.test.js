const babel = require('@babel/core');
const testPlugin = require('./jsx-babel-plugin');
const chai = require("chai");
const chaiJestSnapshot = require("chai-jest-snapshot");

chai.use(chaiJestSnapshot);

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});

describe('jsx-babel-plugin', () => {
    before(function() {
        chaiJestSnapshot.resetSnapshotRegistry();
    });
    const transform = (input, {
        pragma = 'execView',
        throwIfNamespace = false,
        useBuiltIns = true,
        pragmaFrag = 'makeFrag',
        attributesGetterPath = 'utils/attributes-getter',
        childMapperPath = 'utils/child-mapper',
    } = {}) => {
        const { code } = babel.transform(input, {
            plugins: [
                [testPlugin, {
                    pragma,
                    throwIfNamespace,
                    useBuiltIns,
                    pragmaFrag,
                    attributesGetterPath,
                    childMapperPath
                }],
            ]
        });
        return code;
    };

    it('is an empty tag', () => {
        const code = transform(`
                function templateFunction(){
                    return <div />;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with attributes', () => {
        const code = transform(`
                function templateFunction(){
                    return <div required class='block-bundle__smile'/>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with dynamic attributes', () => {
        const code = transform(`
                function templateFunction(){
                    return <div required={isRequired} class='block-bundle__smile'/>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with dynamic attributes & spread operators', () => {
        const code = transform(`
                function templateFunction(){
                    return <div required class='block-bundle__smile' {...props} {...yetAnotherProps}/>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with children', () => {
        const code = transform(`
                function templateFunction(){
                    return <div><br/></div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with html entities', () => {
        const code = transform(`
                function templateFunction(){
                    return <div>&abc&</div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with attributes & children', () => {
        const code = transform(`
                function templateFunction(){
                    return <div required class='block-bundle__smile'><br/></div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with attributes & component children', () => {
        const code = transform(`
                function templateFunction(){
                    return <div required class='block-bundle__smile'><Component/></div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with attributes & variable children', () => {
        const code = transform(`
                function templateFunction(){
                    return <div required class='block-bundle__smile'>{a}{b}{c}</div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with static children', () => {
        const code = transform(`
                function templateFunction(){
                    return <div>{'a'}{'b'}{'c'}</div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with mixed children', () => {
        const code = transform(`
                function templateFunction(){
                    return <div>{a}{'b'}{'c'}</div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a tag with children call', () => {
        const code = transform(`
                function templateFunction(){
                    return <div>{a()}{'b'}{'c'}</div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a fragment', () => {
        const code = transform(`
                function templateFunction(){
                    return <>
                        <div required class='block-bundle__smile'></div>
                        <br/>
                    </>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a complex fragment', () => {
        const code = transform(`
                function templateFunction(type){
                    return <>
                        <div required class={\`block-bundle__smile_type_\${type}\`}></div>
                        <br/>
                        {a}
                        <>
                            <Component />
                            {'b'}
                            {c}
                        </>
                    </>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is an empty component', () => {
        const code = transform(`
                function templateFunction(){
                    return <Component />;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a component with attributes', () => {
        const code = transform(`
                function templateFunction(){
                    return <Component required class='block-bundle__smile'/>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a component with dynamic attributes & spread operators', () => {
        const code = transform(`
                function templateFunction(){
                    return <Component required class='block-bundle__smile' {...props} {...yetAnotherProps}/>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a component with children', () => {
        const code = transform(`
                function templateFunction() {
                    return <Component><Component2/></Component>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a component with children 2', () => {
        const code = transform(`
                function templateFunction() {
                    return <Component><Component2/><Component3/></Component>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a component with attributes & children', () => {
        const code = transform(`
                function templateFunction(){
                    return <Component required class='block-bundle__smile'><Component2/><Component3/></Component>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a component with dynamic attributes & spread operator & children', () => {
        const code = transform(`
                function templateFunction(){
                    return <Component required class='block-bundle__smile' {...props} title={title}><Component2/><Component3/></Component>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is a component with dynamic attributes 2', () => {
        const code = transform(`
                function templateFunction(){
                    return <Component title={<><Component2/><Component3/></>} />;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('should be a paired tag', () => {
        const code = transform(`
                function templateFunction(){
                    return <div />;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('should be a self-closing tag', () => {
        const code = transform(`
                function templateFunction(){
                    return <br />;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('shouldn\'t have children on self-closing tag', () => {
        // code have to be inside expect calling for chai error catch
        chai.expect(() => transform(`
                function templateFunction(){
                    return <br>abacaba</br>;
                }
            `)).to.throw(TypeError);
    });
    it('should be lowercase on non-dynamic attribute', () => {
        const code = transform(`
                function templateFunction(){
                    return <div abaCaba="abacaba"></div>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    describe("view", () => {
        it("should have execView as third params of template function on components", () => {
            const code = transform(`
                function templateFunction(){
                    return <Component abaCaba="abacaba"></Component>;
                }
            `);
            chai.expect(code).to.matchSnapshot();
        });
        it("shouldn't have execView as third params of template function on html elements", () => {
            const code = transform(`
                    function templateFunction(){
                        return <div abaCaba="abacaba"></div>;
                    }
                `);
            chai.expect(code).to.matchSnapshot();
        });
        it('should have third param of template function named as execView', () => {
            // code have to be inside expect calling for chai error catch
            chai.expect(() => transform(`
                    function templateFunction(aba, caba, caba){
                        return <Component abaCaba="abacaba"></Component>;
                    }
                `)).to.throw(Error);
        });
    });
    describe("view.cached", () => {
        it("should have execView as second params of template function on components", () => {
            const code = transform(`
                    cached(function templateFunction(){
                        return <Component abaCaba="abacaba"></Component>;
                    })
                `);
            chai.expect(code).to.matchSnapshot();
        });
        it("shouldn't have execView as third params of template function on html elements", () => {
            const code = transform(`
                    cached(function templateFunction(){
                        return <div abaCaba="abacaba"></div>;
                    })
                `);
            chai.expect(code).to.matchSnapshot();
        });
        it('should have second param of template function named as execView', () => {
            // code have to be inside expect calling for chai error catch
            chai.expect(() => transform(`
                    cached(function templateFunction(aba, caba, caba){
                        return <Component abaCaba="abacaba"></Component>;
                    })
                `)).to.throw(Error);
        });

    });
    describe("template function", () => {
        it('can be arrow function', () => {
            const code = transform(`
                    () => {
                        return <div abaCaba="abacaba"></div>;
                    }
                `);
            chai.expect(() => code).to.not.throw();
        });
        it('can be function expression', () => {
            const code = transform(`
                    cached(function() {
                        return <div abaCaba="abacaba"></div>;
                    });
                `);
            chai.expect(() => code).to.not.throw();
        });
        it('can be function declaration', () => {
            const code = transform(`
                    function func() {
                        return <div abaCaba="abacaba"></div>;
                    }
                `);
            chai.expect(() => code).to.not.throw();
        });
        it('should be outermost', () => {
            const code = transform(`
                    function tmpl2(data) {
                        function elem(num) {
                            return <Component>{num}</Component>;
                        }
                        return [1,2,3].map(elem);
                    }
                `);
            chai.expect(code).to.matchSnapshot();
        });
        it('should be outermost 2', () => {
            const code = transform(`
                    function tmpl1(data) {
                        return [1,2,3].map(num => <Component>{num}</Component>);
                    }
                `);
            chai.expect(code).to.matchSnapshot();
        });
    });
    it('should be without childMapper call expression', () => {
        const code = transform(`
                cached(function() {
                    return <div abaCaba="abacaba">
                    {\`abacaba\`}
                    </div>;
                });
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('should use attribute getter if attribute is member expression', () => {
        const code = transform(`
                function link(data = {}) {
                    return <a href={data.href}>{data.content}</a>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('should not use attribute getter if attribute is not identifier', () => {
        const code = transform(`
                function path() {
                    return <path fill-rule="evenodd" />;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('is no have value if boolean positive attribute', () => {
        const code = transform(`
                function templateFunction(){
                    return <div />;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('object destructing under Identifier', () => {
        const code = transform(`
                function templateFunction(data){
                    return <Component0 {...data}><Card__title /></Component0>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('object destructing under MemberExpression', () => {
        const code = transform(`
                function templateFunction(data){
                    return <Component0 {...data.abacaba}><Card__title /></Component0>;
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
    it('plain string', () => {
        const code = transform(`
                function templateFunction(){
                    return "ababacaba"
                }
            `);
        chai.expect(code).to.matchSnapshot();
    });
});
