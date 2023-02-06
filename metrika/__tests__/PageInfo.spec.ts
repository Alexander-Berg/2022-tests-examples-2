import * as chai from 'chai';
import * as sinon from 'sinon';
import * as guid from '@src/utils/guid';

import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { getPageInfo, TAB_ID_KEY } from '../PageInfo';

describe('PageInfo', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;

    it('Gets base', () => {
        const base = document.createElement('a');
        base.setAttribute('href', 'http://example.com');
        let ctx: any = {
            document: {
                querySelector: sinon.stub().returns(base),
            },
        };
        let pageInfo = getPageInfo(ctx);
        chai.expect(pageInfo.getBase()).to.equal('http://example.com');
        chai.assert(ctx.document.querySelector.calledWith('base[href]'));

        ctx = {
            document: {
                querySelector: sinon.stub().returns(null),
            },
        };
        pageInfo = getPageInfo(ctx);
        chai.expect(pageInfo.getBase()).to.equal(null);
        chai.assert(ctx.document.querySelector.calledWith('base[href]'));
    });

    it('collects doctype', () => {
        const ctx = {
            document: {
                doctype: {
                    name: 'html',
                    publicId: 'pubid',
                    systemId: 'sysid',
                },
            },
        } as any;
        const pageInfo = getPageInfo(ctx);
        chai.expect(pageInfo.getDoctype()).to.equal(
            '<!DOCTYPE html PUBLIC "pubid" "sysid">',
        );
    });

    it('gets tab id', () => {
        const openerGuid = 'opener';
        const oldGuid = 'old';
        const newGuid = 'new';
        const guidStub = sinon.stub(guid, 'getGuid').returns(newGuid);
        let ctx: any = {
            sessionStorage: {
                getItem: sinon.stub().returns(oldGuid),
            },
        };

        let pageInfo = getPageInfo(ctx);
        chai.expect(pageInfo.getTabId()).to.equal(oldGuid);
        chai.assert(ctx.sessionStorage.getItem.calledWith(TAB_ID_KEY));

        ctx = {
            opener: {},
            sessionStorage: {
                setItem: sinon.stub(),
                getItem: sinon.stub().returns(null),
            },
        };
        pageInfo = getPageInfo(ctx);
        chai.expect(pageInfo.getTabId()).to.equal(newGuid);
        chai.assert(ctx.sessionStorage.getItem.calledWith(TAB_ID_KEY));

        ctx = {
            opener: {
                sessionStorage: {
                    getItem: sinon.stub().returns(openerGuid),
                },
            },
            sessionStorage: {
                setItem: sinon.stub(),
                getItem: sinon.stub().returns(openerGuid),
            },
        };
        pageInfo = getPageInfo(ctx);
        chai.expect(pageInfo.getTabId()).to.equal(newGuid);
        chai.assert(ctx.sessionStorage.getItem.calledWith(TAB_ID_KEY));
        chai.assert(ctx.opener.sessionStorage.getItem.calledWith(TAB_ID_KEY));

        ctx = {
            opener: {
                sessionStorage: {
                    getItem: sinon.stub().returns(openerGuid),
                },
            },
            sessionStorage: {
                setItem: sinon.stub(),
                getItem: sinon.stub().returns(oldGuid),
            },
        };
        pageInfo = getPageInfo(ctx);
        chai.expect(pageInfo.getTabId()).to.equal(oldGuid);
        chai.assert(ctx.sessionStorage.getItem.calledWith(TAB_ID_KEY));
        chai.assert(ctx.opener.sessionStorage.getItem.calledWith(TAB_ID_KEY));

        guidStub.restore();
    });
});
