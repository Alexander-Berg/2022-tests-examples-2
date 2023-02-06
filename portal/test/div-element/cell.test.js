const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const {PropertyRequiredError, InvalidInstanceError} = require('../../src/infra').errorTypes;
const {DivCell, DivImage} = require('../../').DivElements;
const {TextStyle, DivSize, DivPosition} = require('../../').Styles;

describe('DivCell element test', () => {
    describe('with valid inputs', () => {
        it('should create empty cell', () => {
            const cell = new DivCell();
            assert.deepEqual(cell.clean, {});
        });

        it('should create cell with text', () => {
            const cell = new DivCell({
                text: ' Сегодня жарко',
                textStyle: TextStyle.TITLE_M

            });
            assert.deepEqual(cell.clean, {
                text: ' Сегодня жарко',
                text_style: 'title_m'
            });
        });

        it('should create cell with image and alignment', () => {
            const cell = new DivCell({
                textStyle: TextStyle.TEXT_S,
                image: new DivImage({
                    ratio:1,
                    url: 'https://storage.mds.yandex.net/get-sport/28639/e723fabf-7d38-4bf9-86b0-d926279b6ca8.png'
                }),
                imageSize: DivSize.XS,
                vertAlign: DivPosition.CENTER

            });
            assert.deepEqual(cell.clean, {
                text_style: 'text_s',
                image: {
                    ratio: 1,
                    type: 'div-image-element',
                    image_url: 'https://storage.mds.yandex.net/get-sport/28639/e723fabf-7d38-4bf9-86b0-d926279b6ca8.png'
                },
                image_size: 'xs',
                vertical_alignment: 'center'
            });
        });
    });

    describe('with invalid inputs', () => {
        it('should throw InvalidInstanceError', () => {
            assert.throws(() => {
                new DivCell({
                    text: ' Сегодня жарко',
                    textStyle: 'title_s'
                });

            }, InvalidInstanceError, 'Invalid instance');

            assert.throws(() => {
                new DivCell({
                    horizAlign: 'center'
                });

            }, InvalidInstanceError, 'Invalid instance');
        });
    });
});