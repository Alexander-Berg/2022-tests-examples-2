const config = require('../../../../configs/current');
const expect = require('expect.js');
const rumInit = require('../../../../lib/rum-counter/init').rumInit;

const RUM_ID = 'ru.1207.auth';
const REGION_ID = 99;
const REQUEST_ID = 1;
const EXPERIMENTS_FLAGS = ['exp.1', 'exp.2'];
const PAGE_ID = '/auth/list';
const PLATFORM = 'desktop';
const VERSION = config.version;

describe('rumInit', () => {
    it('should return init script with custom configs', () => {
        const config = {
            page: PAGE_ID,
            rumId: RUM_ID,
            regionId: REGION_ID,
            requestId: REQUEST_ID,
            slots: EXPERIMENTS_FLAGS,
            platform: PLATFORM,
            version: VERSION,
            experiments: EXPERIMENTS_FLAGS.join(';')
        };

        expect(rumInit(config)).to.be(
            String(`
        Ya.Rum.init({
			"beacon":true,
			"clck":"https:\\u002F\\u002Fyandex.ru\\u002Fclck\\u002Fclick",
			"slots":["exp.1","exp.2"],
			"reqid":${REQUEST_ID}
        }, {
            "region":${REGION_ID},
            "rum_id":"${RUM_ID}",
            "-project":"passport",
            "-page":"\\u002Fauth\\u002Flist",
            "-env":"${process.env.NODE_ENV}",
            "-platform":"${PLATFORM}",
            "-version":"${VERSION}",
            "experiments":"${EXPERIMENTS_FLAGS.join(';')}"
        });
        Ya.Rum.observeDOMNode('2876', '.layout');
    `).replace(/\n|\s{2,}/g, '')
        );
    });
});
