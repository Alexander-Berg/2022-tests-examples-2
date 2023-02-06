import {document__customs, document} from './document.view.js';
import {expect} from "chai";
import chai from "chai";
import {execView} from "lib/home.view";

describe('document', () => {
    describe('document__customs', () => {
        it('should return desktop if no uatraits', () => {
            expect(document__customs(null, {
                uatraits: {}
            })).to.equal('i-ua_browser_desktop1');
        });
    });
    it('should render', () => {
        chai.expect(execView(document, {
            uatraits: {},
            getStaticURL: {
                getAbsolute: () => {},
            },
            l10n: () => {},
        })).to.matchSnapshot();
    });
});