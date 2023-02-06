import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Ads } from '@lib/utils/ads';

// todo move to imports

describe('teaser', function() {
    it('returns html teaser', function() {
        let req = mockReq({}, {
            ads: new Ads({
                Banners: {
                    banners: {
                        teaser: {
                            html: '<div>Html from yabs</div>',
                            linknext: '+teaser'
                        }
                    },
                    pixelBase: 'https://pixel.base/path/',
                    displayed: null
                }
            }),
            Teaser: {
                show: 1
            }
        });
        let etalon;

        etalon = '<div  class="teaser i-bem" role="complementary" aria-label="Реклама" data-bem="{&quot;teaser&quot;:{}}">' +
                '<div class=\'teaser__content\'>' +
                    '<div>Html from yabs</div>' +
                '</div>' +
            '</div>';

        expect(execView('Teaser', req)).toEqual(etalon);
    });

    describe('triming by teaser__rtrim', function() {
        let etalon = 'This is test message. These words should be untouchable: nbsp, ensp, emsp, thinsp.';
        let phrasesWithUnicodeSpaces = '             '.split('').map(function(space) {
            return etalon + space;
        });

        let phrasesWithEntitySpaces = ['&nbsp;', '&ensp;', '&emsp;', '&thinsp;'].map(function(space) {
            return etalon + space;
        });

        it('trims string with unicode', function() {
            phrasesWithUnicodeSpaces.forEach(function(phrase) {
                expect(execView('Teaser__rtrim', phrase)).toEqual(etalon);
            });
        });

        it('trims string with html entity', function() {
            phrasesWithEntitySpaces.forEach(function(phrase) {
                expect(execView('Teaser__rtrim', phrase)).toEqual(etalon);
            });
        });
    });
});
