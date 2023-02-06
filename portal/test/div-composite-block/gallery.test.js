const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const DivCard = require('../../index');
const Action = DivCard.Action;
const {DivTail, DivIcon} = DivCard.LightBlocks;
const {Table, Universal, Image, Separator} = DivCard.Blocks;
const {DivContainer, DivGallery} = DivCard.CompositeBlocks;
const {BorderStyle, DivDirection, NumericSize, TextStyle, DivPosition, DivSize} = DivCard.Styles;
const {DivFrame, DivImage, DivColumn, DivRow, DivCell} = DivCard.DivElements;
const {PropertyRequiredError, InvalidInstanceError} = DivCard.Infra.errorTypes;
const {sport_gallery} = require('../mocks');

describe('Div Gallery test', () => {
    describe('#createGallery', () => {
        describe('with valid inputs', () => {
            it('should create simple gallery with one item', () => {
                const gallery = new DivGallery({
                    items: [new DivContainer({
                        children: [
                            new Separator()
                        ],
                        width: new NumericSize(4),
                        height: new NumericSize(1)
                    })]
                });

                assert.deepEqual(gallery.clean, {
                        "type": "div-gallery-block",
                        "items": [{
                            "type": "div-container-block",
                            "children": [{"type": "div-separator-block", "has_delimiter": 0}],
                            "width": {"value": 4, "type": "numeric"},
                            "height": {"value": 1, "type": "numeric"}
                        }]
                    }
                );
            });

            it('should create complicate gallery', () => {
                const gallery = new DivGallery({
                    paddingBottom: new NumericSize(1),
                    paddingTop: new NumericSize(2),
                    paddingBetweenItems: new NumericSize(0),
                    tail: new DivTail({
                        text: 'Спорт',
                        textColor: '#000000',
                        icon: new DivIcon({
                            fillColor: '#eef2f6',
                            iconColor: '#000000',
                            borderColor: '#00ffffff'
                        }),
                        action: new Action({
                            id: 'sport_tail',
                            url: 'yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fsport%3Fsource%3Dyandex_portal%26utm_source%3Dyandex_portal%26lat%3D55.73%26lng%3D37.59%26appsearch_header%3D1'
                        })
                    }),
                    items: [new DivContainer({
                        children: [
                            new Image({
                                image: new DivImage({
                                    ratio: 2,
                                    url: 'https://avatars.mds.yandex.net/get-ynews/138655/1b242f132c7ea1233b2927d3c1af2d6a/563x304'
                                }),
                            }),
                            new Universal({
                                text: 'title',
                                textColor: '#333333',
                                textMaxLines: 5,
                                titleMaxLines: 4,
                                titleStyle: TextStyle.TITLE_S,
                                textStyle: TextStyle.TEXT_M
                            }),
                            new Separator({
                                hasDelimiter: true,
                                size: DivSize.XXS
                            }),
                            new Table({
                                columns: [
                                    new DivColumn({
                                        weight: 1,
                                        leftPadding: DivSize.ZERO
                                    }),
                                    new DivColumn({
                                        leftPadding: DivSize.XXS,
                                        rightPadding: DivSize.ZERO
                                    })
                                ],
                                rows: [
                                    new DivRow({
                                        topPadding: DivSize.S,
                                        bottomPadding: DivSize.XXS,
                                        cells: [
                                            new DivCell({
                                                textStyle: TextStyle.TEXT_S,
                                                imageSize: DivSize.XXS,
                                                vertAlign: DivPosition.CENTER,
                                                text:  'Канал спорта' ,
                                                textColor: '#939cbo'
                                            }),
                                            new DivCell({
                                                textStyle: TextStyle.TEXT_S,
                                                imageSize: DivSize.XS,
                                                vertAlign: DivPosition.CENTER,
                                                image: new DivImage({
                                                    ratio: 1,
                                                    url: 'https://storage.mds.yandex.net/get-sport/28639/e723fabf-7d38-4bf9-86b0-d926279b6ca8.png'
                                                })
                                            })
                                        ]
                                    })
                                ]
                            })
                        ],
                        direction: DivDirection.VERTICAL,
                        width: new NumericSize(244),
                        height: new NumericSize(240),
                        vertAlign: DivPosition.TOP,
                        frame: new DivFrame({
                            style: BorderStyle.SHADOW
                        })
                    })]
                });
                assert.deepEqual(gallery.clean, sport_gallery);
            });
        });

        describe('with invalid inputs', () => {
            it('should throw PropertyRequiredError if items is not defined', () => {
                assert.throws(() => {
                    new DivGallery({});
                }, PropertyRequiredError, 'Property: items is required');
            });

            it('should throw InvalidInstanceError if one of the children\'s element is not instance of DivContainer',
                () => {
                    assert.throws(() => {
                        new DivGallery({
                            items: [1]
                        });
                    }, InvalidInstanceError, 'Invalid instance. An object must be an instance of DivContainer');
                });
        });
    });
});