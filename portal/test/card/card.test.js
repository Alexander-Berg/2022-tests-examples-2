const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const DivCard = require('../../');
const Card = DivCard.Card;
const {State, States} = require('../../src/state');
const {Blocks, DivItem, DivTail, DivIcon, DivTitle} = require('../../src/div');
const {Action, Url, SchemeTypes} = DivCard;
const {MenuItem} = DivCard.LightBlocks;
const {Title, Image} = DivCard.Blocks;
const {DivTabs, DivContainer, DivGallery} = DivCard.CompositeBlocks;
const {PropertyRequiredError, InvalidInstanceError} = DivCard.Infra.errorTypes;
const {BorderStyle, DivDirection, PredefinedSize, NumericSize, TextStyle, DivPosition, BackgroundTypes, Backgrounds} = DivCard.Styles;
const {DivFrame, DivImage} = DivCard.DivElements;
const {sport} = require('../mocks');

describe('Div card test', () => {
    describe('#createCard', () => {
        let card, cardParams;

        before(() => {
            const states = new States();
            states.add(new State({id: 1, blocks: new Blocks()}));
            cardParams = {
                id: 'sport',
                topic: 'sport_card',
            };

            card = new Card({
                ...cardParams,
                states: states
            });
        });

        describe('with valid inputs', () => {
            it('should create card with given id', () => {
                assert.deepEqual(card.id, 'sport');
            });

            it('should create card with given topic', () => {
                assert.deepEqual(card.topic, 'sport_card');
            });

            it('should create card with one state', () => {
                assert.deepEqual(card.data.states.length, 1);
            });

            it('should add second state to card', () => {
                card.addState(new State({id: 2}));
                assert.deepEqual(card.data.states[1], {
                    state_id: 2,
                    blocks: []
                });
            });

            it('should create sport card', () => {

                card = new Card({
                    id: 'sport',
                    topic: 'sport_card',
                    utime: 1554116300,
                    ttl: 300,
                    ttv: 1200,
                    menu: {},
                    title: 'Новости спорта'
                });

                const state = new State({id: 1});
                const title = new Title({
                    text: '<font color=\"#000000\">Спорт</font>',
                    menuItems: [

                        new MenuItem({
                            url: new Url({
                                scheme: SchemeTypes.OPENSETTINGS,
                                query: {
                                    screen: 'feed'
                                }
                            }),
                            text: "Настройки ленты"

                        }),
                        new MenuItem({
                            url: new Url({
                                scheme: SchemeTypes.HIDECARD,
                                query: {
                                    topic_card_ids: 'sport_card',
                                    undo_snackbar_text: 'Вы скрыли карточку'
                                }
                            }),
                            text: "Скрыть карточку"

                        })
                    ],
                    menuColor: '#000000',
                    textStyle: TextStyle.TITLE_M


                });

                const containerBg = new Backgrounds();

                containerBg.add(BackgroundTypes.GRADIENT({
                    start: '#ffffff',
                    end: '#eef2f6'
                }));

                const gallery = new DivGallery({
                    paddingBottom: new NumericSize(1),
                    paddingTop: new NumericSize(2),
                    paddingBetweenItems: new NumericSize(0),
                    tail: new DivTail({
                        text: 'Другие новости спорта',
                        textStyle: TextStyle.TEXT_M,
                        icon: new DivIcon({
                            fillColor: '#eef2f6',
                            iconColor: '#000000',
                            borderColor: '#00ffffff'
                        }),
                        action: new Action({
                            id: 'sport_tail',
                            url: new Url({
                                scheme: SchemeTypes.YELLOWSKIN,
                                query: {
                                    background_color: '#4b9645',
                                    buttons_color: '#ffffff',
                                    omnibox_color: '#288736',
                                    status_bar_theme: 'dark',
                                    text_color: '#ffffff',
                                    url: new Url({
                                        scheme: SchemeTypes.HTTPS,
                                        host: 'yandex.ru',
                                        path: 'sport',
                                        query: {
                                            source: 'yandex_portal',
                                            utm_source: 'yandex_portal',
                                            lat: '55.73',
                                            lng: '37.59',
                                            appsearch_header: 1
                                        }

                                    }).value

                                }
                            })
                        }),
                        items: [
                            new DivContainer({
                                height: new NumericSize(240),
                                width: new NumericSize(244),
                                direction: DivDirection.VERTICAL,
                                frame: new DivFrame({
                                    style: BorderStyle.SHADOW
                                }),
                                vertAlign: DivPosition.VERTICAL,
                                background: containerBg,
                                children: [
                                    new DivImage({
                                        ratio: 2,
                                        url: 'https://avatars.mds.yandex.net/get-ynews/138655/1b242f132c7ea1233b2927d3c1af2d6a/563x304'
                                    })
                                ]
                            })
                        ]
                    }),
                    items: [
                        new DivContainer({
                            children: [
                                new Image({
                                    image: new DivImage({
                                        ratio: 2,
                                        url: 'https://avatars.mds.yandex.net/get-ynews/138655/1b242f132c7ea1233b2927d3c1af2d6a/563x304'
                                    }),
                                })
                            ],
                            direction: DivDirection.VERTICAL,
                            width: new NumericSize(244),
                            height: new NumericSize(240),
                            vertAlign: DivPosition.TOP,
                            frame: new DivFrame({
                                style: BorderStyle.SHADOW
                            }),
                            background: containerBg
                        })
                    ]
                });

                const tabs = new DivTabs({
                    items: [
                        new DivItem({
                            title: new DivTitle({
                                text: 'ВСЕ',
                                action: new Action({
                                    id: 'sport_all',
                                    url: 'yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fyandex.ru%2Fsport%3Ffrom%3Dhome%26utm_campaign%3D%26utm_content%3Dall_posts%26utm_medium%3Dpromoblock%26utm_source%3Dappsearch%26appsearch_header%3D1'
                                })
                            }),
                            content: new DivContainer({
                                children: [
                                    gallery
                                ],
                                direction: DivDirection.VERTICAL,
                                width: new PredefinedSize(PredefinedSize.MATH_PARENT),
                                height: new NumericSize(260),
                                frame: new DivFrame({
                                    style: BorderStyle.SHADOW
                                }),
                                vertAlign: DivPosition.TOP
                            })
                        }),
                        new DivItem({
                            title: new DivTitle({
                                text: 'ФУТБОЛ',
                                action: new Action({
                                    url: 'yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fsport%3Fsource%3Dyandex_portal%26utm_source%3Dyandex_portal%26lat%3D55.73%26lng%3D37.59%26appsearch_header%3D1',
                                    id: 'sport_all'
                                })
                            }),
                            content: new DivContainer({
                                children: [
                                    gallery
                                ],
                                direction: DivDirection.VERTICAL,
                                width: new PredefinedSize(PredefinedSize.MATH_PARENT),
                                height: new NumericSize(300),
                                vertAlign: DivPosition.TOP
                            })
                        })
                    ],
                    inactiveTabColor: '#CC000000'
                });

                state.addBlock(title);
                state.addBlock(tabs);
                card.addState(state);
                card.addBackground(BackgroundTypes.SOLID('#ffffff'));

                assert.deepEqual(card.clean, sport);
            });

            it('should create card with menu', () => {
                var card = new Card({id: 'sport', utime: 1});
                card.setMenuColor('#b0b0b0');
                card.addMenuItem({
                    action: new Url({
                        scheme: 'https',
                        host: 'ya.ru'
                    }),
                    text: 'click'
                });
                assert.deepEqual(card.clean, {
                    data: {
                        background: [],
                        states: []
                    },
                    id: 'sport',
                    type: 'div',
                    utime: 1,
                    menu: {
                        menu_list: [
                            {
                                action: 'https://ya.ru',
                                text: 'click'
                            }],
                        button_color: '#b0b0b0'
                    }
                });
            });
        });

        describe('with invalid inputs', () => {
            it('should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new Card();
                }, PropertyRequiredError, 'Property: id is required');
            });

            it('should throw InvalidInstanceError', () => {
                assert.throws(() => {
                    new Card({...cardParams, states: []});
                }, InvalidInstanceError, 'Invalid instance. An object must be an instance of States.');
                assert.throws(() => {
                    new Card({...cardParams, background: []});
                }, InvalidInstanceError, 'Invalid instance. An object must be an instance of Backgrounds.');
            });
        });
    });
});