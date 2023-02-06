import chai from 'chai';
import sinon from 'sinon';
import * as hidden from '@src/utils/webvisor/isHiddenContent';
import * as inputUtils from '@src/utils/webvisor/inputUtils';
import * as array from '@src/utils/array';
import {
    collectNodeInfo,
    PASSWORD_PLACEHOLDER,
    b64imagePlaceholder,
} from '../collectNodeInfo';

describe('collectNodeInfo', () => {
    const ctx = {
        document: {
            documentElement: {
                attributes: [{ name: 'attr', value: '1' }],
                nodeName: 'html',
                previousSibling: {},
                nextSibling: {},
            },
        },
        Array,
    } as any;
    const nonEUDisabledForms = {
        isEU: false,
        recordForms: true,
    } as any;
    const nonEUoptions = {
        isEU: false,
        recordForms: true,
    } as any;
    const euOptions = {
        isEU: true,
        recordForms: true,
    } as any;
    const id = 3;
    const parentId = 123;
    const prevId = 1;
    const nextId = 2;
    const scrambledContent = 'scramble';

    let isHiddenStub: sinon.SinonStub<any, any>;
    let obfuscationNeeded: sinon.SinonStub<any, any>;
    let isHiddenInputStub: sinon.SinonStub<any, any>;
    let isValidInputStub: sinon.SinonStub<any, any>;
    let forceRecordEnables: sinon.SinonStub<any, any>;
    let isPasswordStub: sinon.SinonStub<any, any>;

    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        isHiddenInputStub = sandbox
            .stub(inputUtils, 'isPrivateInformationField')
            .returns(false);
        isValidInputStub = sandbox
            .stub(inputUtils, 'isValidInput')
            .returns(false);
        obfuscationNeeded = sandbox
            .stub(inputUtils, 'isObfuscationNeeded')
            .returns({
                obfuscationNeeded: false,
                isPrivate: false,
                forceRecord: false,
            });
        isPasswordStub = sandbox
            .stub(inputUtils, 'isPasswordField')
            .returns(false);
        sandbox.stub(array, 'toArray').callsFake((a: any) => a);
        sandbox.stub(hidden, 'scrambleContent').returns(scrambledContent);
        isHiddenStub = sandbox.stub(hidden, 'isHiddenContent').returns(false);
        forceRecordEnables = sandbox
            .stub(inputUtils, 'isForceRecordingEnabled')
            .returns(false);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('collects text node info', () => {
        const node = {
            nodeName: '#text',
            textContent: 'some content',
            nodeType: 3,
        } as any;
        isHiddenStub.returns(false);
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            name: '#text',
            content: 'some content',
            attributes: {},
            node,
        });
    });

    it('sets force content', () => {
        const node = {
            nodeName: '#text',
            textContent: 'some content',
            nodeType: 3,
        } as any;
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
            {},
            'forced content',
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            name: '#text',
            content: 'forced content',
            node,
            attributes: {},
        });
    });

    it('scrambles hidden text node content', () => {
        const node = {
            nodeName: '#text',
            textContent: 'some content',
            nodeType: 3,
        } as any;
        isHiddenStub.returns(true);
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            hidden: true,
            parent: parentId,
            name: '#text',
            content: scrambledContent,
            attributes: {},
            node,
        });
    });

    it('collects regular node info', () => {
        const node = {
            attributes: [
                { name: 'class', value: 'some-class' },
                { name: 'id', value: 'some-id' },
                { name: 'some-attr', value: 'val1' },
                { name: 'overrided-attr', value: 'old' },
            ],
            nodeName: 'div',
            namespaceURI: 'svg-namespace',
        } as any;
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            3,
            parentId,
            1,
            2,
            {
                'overrided-attr': 'new',
            },
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id: 3,
            prev: 1,
            next: 2,
            parent: parentId,
            attributes: {
                class: 'some-class',
                id: 'some-id',
                'some-attr': 'val1',
                'overrided-attr': 'new',
            },
            name: 'div',
            node,
            namespace: 'svg-namespace',
        });
    });

    it('collects image src', () => {
        const node = {
            attributes: [{ name: 'src', value: 'src' }],
            src: 'correct-src',
            nodeName: 'IMG',
            getAttribute: sandbox.stub().withArgs('srcset').returns(''),
        } as any;
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {
                src: 'correct-src',
            },
            name: 'img',
            node,
        });
    });

    it('replaces hidden image src and records width and height', () => {
        const rect = { width: 100, height: 200 };
        const node = {
            attributes: [{ name: 'src', value: 'src' }],
            currentSrc: 'correct-src',
            nodeName: 'IMG',
            getBoundingClientRect: () => rect,
        } as any;
        isHiddenStub.returns(true);
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            hidden: true,
            attributes: {
                src: b64imagePlaceholder,
                width: 100,
                height: 200,
            },
            name: 'img',
            node,
        });
    });

    it('use image currentSrc if has srcset', () => {
        const node = {
            attributes: [{ name: 'src', value: 'src' }],
            currentSrc: 'correct-currentSrc',
            src: 'correct-src',
            nodeName: 'IMG',
            getAttribute: sandbox
                .stub()
                .withArgs('srcset')
                .returns('correct-srcset'),
        } as any;
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {
                src: 'correct-currentSrc',
            },
            name: 'img',
            node,
        });
    });

    it('collects inputs value', () => {
        const node = {
            type: 'text',
            attributes: [{ name: 'value', value: 'some-value' }],
            currentSrc: 'correct-src',
            nodeName: 'INPUT',
        } as any;
        isValidInputStub.returns(true);
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {
                value: 'some-value',
            },
            name: 'input',
            node,
        });

        const strangeNode = {
            type: 'text',
            attributes: [{ name: 'value', value: 'some-value' }],
            currentSrc: 'correct-src',
            nodeName: 'INPUT',
            value: 'another-value',
        } as any;
        const strangeNodeInfo = collectNodeInfo(
            ctx,
            strangeNode,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );
        chai.expect(strangeNodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {
                value: 'another-value',
            },
            name: 'input',
            node: strangeNode,
        });
    });

    it('collects checked from checkbox', () => {
        const node = {
            type: 'checkbox',
            getAttribute: (name: string) =>
                name === 'type' ? 'checkbox' : null,
            attributes: [{ name: 'checked', value: null }],
            checked: true,
            nodeName: 'INPUT',
        } as any;
        isValidInputStub.returns(true);
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUoptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {
                checked: 'checked',
            },
            name: 'input',
            node,
        });
    });

    it('ignores password-like attributes on a password field', () => {
        isPasswordStub.returns(true);
        const node = {
            type: 'password',
            attributes: [
                { pwd: 'value', password: '123', initialValue: 'something' },
            ],
            nodeName: 'INPUT',
        } as any;
        const options = {
            isEU: false,
            recordForms: true,
        };
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            options,
            id,
            parentId,
            prevId,
            nextId,
        );
        chai.expect(nodeInfo).to.deep.equal({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {},
            name: 'input',
            node,
        });
    });

    it('records forms only if forced if recordForms is false', () => {
        isHiddenInputStub.returns(false);
        isValidInputStub.returns(true);
        isHiddenStub.returns(false);
        const options = {
            isEU: false,
            recordForms: false,
        };
        const node = {
            type: 'text',
            attributes: [{ name: 'value', value: '123' }],
            nodeName: 'INPUT',
        } as any;

        let nodeInfo = collectNodeInfo(
            ctx,
            node,
            options,
            id,
            parentId,
            prevId,
            nextId,
        );
        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {
                value: `${PASSWORD_PLACEHOLDER}${PASSWORD_PLACEHOLDER}${PASSWORD_PLACEHOLDER}`,
            },
            name: 'input',
            node,
        });

        forceRecordEnables.returns(true);
        nodeInfo = collectNodeInfo(
            ctx,
            node,
            options,
            id,
            parentId,
            prevId,
            nextId,
        );
        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {
                value: `123`,
            },
            name: 'input',
            node,
        });
    });

    it('blures private field in eu counters', () => {
        const node = {
            type: 'text',
            attributes: [{ name: 'value', value: '123' }],
            nodeName: 'INPUT',
        } as any;
        obfuscationNeeded.returns({
            obfuscationNeeded: true,
            isPrivate: true,
            forceRecord: false,
        });
        isHiddenInputStub.returns(true);
        isValidInputStub.returns(true);
        let nodeInfo = collectNodeInfo(
            ctx,
            node,
            euOptions,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            hidden: true,
            parent: parentId,
            attributes: {
                value: `${PASSWORD_PLACEHOLDER}${PASSWORD_PLACEHOLDER}${PASSWORD_PLACEHOLDER}`,
            },
            name: 'input',
            node,
        });

        nodeInfo = collectNodeInfo(
            ctx,
            node,
            nonEUDisabledForms,
            id,
            parentId,
            prevId,
            nextId,
        );

        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            hidden: true,
            parent: parentId,
            attributes: {
                value: `${PASSWORD_PLACEHOLDER}${PASSWORD_PLACEHOLDER}${PASSWORD_PLACEHOLDER}`,
            },
            name: 'input',
            node,
        });
    });

    it('replaces href for <a> node', () => {
        const link = {
            attributes: [{ name: 'href', value: 'http://example.com' }],
            nodeName: 'A',
        } as any;

        const nodeInfo = collectNodeInfo(
            ctx,
            link,
            euOptions,
            id,
            parentId,
            prevId,
            nextId,
        );
        chai.expect(nodeInfo).to.be.deep.eq({
            id: 3,
            prev: 1,
            next: 2,
            parent: parentId,
            attributes: {
                href: `#`,
            },
            name: 'a',
            node: link,
        });
    });

    it('ignores some attributes', () => {
        const node = {
            attributes: [
                { name: 'srcset', value: 'data1' },
                { name: 'integrity', value: 'data2' },
                { name: 'crossorigin', value: 'data3' },
                { name: 'onclick', value: 'data4' },
                { name: 'password', value: 'data5' },
            ],
            nodeName: 'div',
        } as any;
        const nodeInfo = collectNodeInfo(
            ctx,
            node,
            euOptions,
            id,
            parentId,
            prevId,
            nextId,
        );
        chai.expect(nodeInfo).to.be.deep.eq({
            id,
            prev: prevId,
            next: nextId,
            parent: parentId,
            attributes: {},
            name: 'div',
            node,
        });
    });
});
