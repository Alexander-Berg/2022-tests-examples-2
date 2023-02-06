import { execView } from '@lib/views/execView';

// todo move to imports

describe('common divjson2', function() {
    let error: jest.SpyInstance;

    beforeEach(function() {
        error = jest.spyOn(home, 'error').mockImplementation(() => undefined);
    });

    afterEach(function() {
        error.mockRestore();
    });

    it('should check data', function() {
        expect(execView('Divjson2__check', null)).toEqual('Missing object');
        expect(execView('Divjson2__check', undefined)).toEqual('Missing object');
        expect(execView('Divjson2__check', {})).toEqual('Missing object');

        expect(execView('Divjson2__check', {
            json: {}
        })).toEqual('Missing card');
        expect(execView('Divjson2__check', {
            json: {
                states: [{
                    state_id: 0,
                    div: {}
                }]
            }
        })).toEqual('Missing card');

        expect(execView('Divjson2__check', {
            json: {
                card: {
                    states: [{
                        state_id: 0,
                        div: {}
                    }]
                }
            }
        })).toEqual('ok');

        expect(execView('Divjson2__check', {
            json: {
                templates: {
                    some: {
                        type: 'checkbox'
                    }
                },
                card: {
                    states: [{
                        state_id: 0,
                        div: {
                            type: 'text'
                        }
                    }]
                }
            }
        })).toEqual('Unknown type "checkbox"');

        expect(execView('Divjson2__check', {
            json: {
                templates: {
                    some: {
                        type: 'checkbox'
                    }
                },
                card: {
                    states: [{
                        state_id: 0,
                        div: {
                            type: 'text'
                        }
                    }]
                }
            }
        })).toEqual('Unknown type "checkbox"');

        expect(execView('Divjson2__check', {
            json: {
                templates: {
                    'home:link': {
                        type: 'text'
                    }
                },
                card: {
                    states: [{
                        state_id: 0,
                        div: {
                            type: 'text'
                        }
                    }]
                }
            }
        })).toEqual('Reserved template name "home:link"');

        expect(execView('Divjson2__check', {
            json: {
                templates: {
                    gif: {
                        type: 'text'
                    }
                },
                card: {
                    states: [{
                        state_id: 0,
                        div: {
                            type: 'text'
                        }
                    }]
                }
            }
        })).toEqual('Template name collision "gif"');

        expect(execView('Divjson2__check', {
            json: {
                card: {
                    states: [{
                        state_id: 0,
                        div: {
                            type: 'container',
                            items: [{
                                type: 'tabs',
                                items: [{
                                    title: 'a',
                                    div: {
                                        type: 'something'
                                    }
                                }]
                            }]
                        }
                    }]
                }
            }
        })).toEqual('Unknown type "something"');

        expect(execView('Divjson2__check', {
            json: {
                templates: {
                    some: {
                        type: 'container'
                    },
                    some2: {
                        type: 'some'
                    }
                },
                card: {
                    states: [{
                        state_id: 0,
                        div: {
                            type: 'text'
                        }
                    }]
                }
            }
        })).toEqual('ok');

        expect(error.mock.calls).toHaveLength(0);
    });

    it('should log incorrect type', function() {
        expect(execView('Divjson2__block', {
            templates: {
            },
            json: {
                type: 'some'
            },
            context: {},
            layoutName: 'test'
        })).toEqual('');

        expect(error.mock.calls).toHaveLength(1);

        expect(error.mock.calls[0]).toEqual([{
            block: 'divjson2-block',
            message: 'Unknown element type',
            source: 'test',
            meta: {
                type: 'some'
            }
        }]);
    });

    describe('templates', function() {
        it('should work', function() {
            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        $text: 'abcde'
                    }
                },
                json: {
                    type: 'some',
                    abcde: 'Lorem'
                },
                context: {}
            })).toEqual({
                context: {
                    abcde: 'Lorem'
                },
                json: {
                    type: 'text',
                    text: 'Lorem',
                    abcde: 'Lorem'
                }
            });

            expect(error.mock.calls).toHaveLength(0);
        });

        it('should work with context from outer block', function() {
            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        $text: 'abcde'
                    }
                },
                json: {
                    type: 'some'
                },
                context: {
                    abcde: 'Lorem'
                }
            })).toEqual({
                context: {
                    abcde: 'Lorem'
                },
                json: {
                    type: 'text',
                    text: 'Lorem'
                }
            });

            expect(error.mock.calls).toHaveLength(0);
        });

        it('should override props', function() {
            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        $text: 'abcde',
                        font_size: 12
                    }
                },
                json: {
                    type: 'some',
                    font_size: 14,
                    abcde: 'Lorem'
                }
            })).toEqual({
                context: {
                    abcde: 'Lorem',
                    font_size: 14
                },
                json: {
                    type: 'text',
                    text: 'Lorem',
                    font_size: 14,
                    abcde: 'Lorem'
                }
            });

            expect(error.mock.calls).toHaveLength(0);
        });

        it('should not use __proto__', function() {
            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: JSON.parse('{"type":"text","$text":"abcde","__proto__":456}')
                },
                json: JSON.parse('{"type":"some","abcde":"Lorem","__proto__":123}'),
                context: {}
            })).toEqual({
                context: {
                    abcde: 'Lorem'
                },
                json: {
                    type: 'text',
                    text: 'Lorem',
                    abcde: 'Lorem'
                }
            });
        });

        it('should not change templates or context', function() {
            let templates = {
                some: {
                    type: 'text',
                    $text: 'abcde',
                    font_size: 12,
                    $line_height: 'lh'
                }
            };

            let context = {
                lh: 1.3
            };

            expect(execView('Divjson2__applyTemplate', {
                templates,
                json: {
                    type: 'some',
                    abcde: 'Lorem'
                },
                context
            })).toEqual({
                context: {
                    lh: 1.3,
                    abcde: 'Lorem'
                },
                json: {
                    type: 'text',
                    text: 'Lorem',
                    abcde: 'Lorem',
                    font_size: 12,
                    line_height: 1.3
                }
            });

            expect(templates).toEqual({
                some: {
                    type: 'text',
                    $text: 'abcde',
                    font_size: 12,
                    $line_height: 'lh'
                }
            });

            expect(context).toEqual({
                lh: 1.3
            });

            expect(error.mock.calls).toHaveLength(0);
        });

        it('should process default template values', function() {
            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        text: 'default',
                        $text: 'abcde'
                    }
                },
                json: {
                    type: 'some'
                },
                context: {},
                layoutName: 'test'
            })).toEqual({
                context: {},
                json: {
                    type: 'text',
                    text: 'default'
                }
            });

            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        $text: 'abcde',
                        text: 'default'
                    }
                },
                json: {
                    type: 'some'
                },
                context: {},
                layoutName: 'test'
            })).toEqual({
                context: {},
                json: {
                    type: 'text',
                    text: 'default'
                }
            });

            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        $text: 'abcde',
                        text: 'default'
                    }
                },
                json: {
                    type: 'some',
                    abcde: 'Lorem'
                },
                context: {},
                layoutName: 'test'
            })).toEqual({
                context: {
                    abcde: 'Lorem'
                },
                json: {
                    type: 'text',
                    text: 'Lorem',
                    abcde: 'Lorem'
                }
            });

            expect(error.mock.calls).toHaveLength(2);

            expect(error.mock.calls[0]).toEqual([{
                block: 'divjson2-block',
                level: 'warn',
                message: 'Missing template field',
                source: 'test',
                meta: {
                    key: '$text',
                    template: 'some'
                }
            }]);

            expect(error.mock.calls[1]).toEqual([{
                block: 'divjson2-block',
                level: 'warn',
                message: 'Missing template field',
                source: 'test',
                meta: {
                    key: '$text',
                    template: 'some'
                }
            }]);
        });

        it('should not override values from previous template', function() {
            expect(execView('Divjson2__applyTemplates', {
                templates: {
                    some: {
                        type: 'text',
                        text: 'Lorem',
                        $font_size: 'font_size',
                        $max_lines: 'max_lines'
                    },
                    some2: {
                        type: 'some',
                        font_size: 12,
                        max_lines: 2
                    },
                    some3: {
                        type: 'some2',
                        font_size: 14
                    }
                },
                json: {
                    type: 'some3',
                    font_size: 16,
                    max_lines: 3
                },
                context: {}
            })).toEqual({
                context: {
                    font_size: 16,
                    max_lines: 3
                },
                json: {
                    type: 'text',
                    text: 'Lorem',
                    font_size: 16,
                    max_lines: 3
                }
            });

            expect(execView('Divjson2__applyTemplates', {
                templates: {
                    some: {
                        type: 'text',
                        text: 'Lorem',
                        $font_size: 'font_size',
                        $max_lines: 'max_lines'
                    },
                    some2: {
                        type: 'some',
                        font_size: 12,
                        max_lines: 2
                    },
                    some3: {
                        type: 'some2',
                        font_size: 14
                    }
                },
                json: {
                    type: 'some3'
                },
                context: {}
            })).toEqual({
                context: {
                    font_size: 14,
                    max_lines: 2
                },
                json: {
                    type: 'text',
                    text: 'Lorem',
                    font_size: 14,
                    max_lines: 2
                }
            });

            expect(error.mock.calls).toHaveLength(0);
        });

        it('should process inner template values', function() {
            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        inner: {
                            $text: 'abcde'
                        }
                    }
                },
                json: {
                    type: 'some',
                    abcde: 'Lorem'
                },
                context: {}
            })).toEqual({
                context: {
                    abcde: 'Lorem'
                },
                json: {
                    type: 'text',
                    inner: {
                        text: 'Lorem'
                    },
                    abcde: 'Lorem'
                }
            });

            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        inner: [{
                            $text: 'abcde'
                        }, {
                            text: 'sub'
                        }]
                    }
                },
                json: {
                    type: 'some',
                    abcde: 'Lorem'
                },
                context: {}
            })).toEqual({
                context: {
                    abcde: 'Lorem'
                },
                json: {
                    type: 'text',
                    inner: [{
                        text: 'Lorem'
                    }, {
                        text: 'sub'
                    }],
                    abcde: 'Lorem'
                }
            });

            expect(error.mock.calls).toHaveLength(0);
        });

        it('should work with nulls', function() {
            expect(execView('Divjson2__applyTemplate', {
                templates: {
                    some: {
                        type: 'text',
                        prop: null
                    }
                },
                json: {
                    type: 'some',
                    prop2: null
                },
                context: {}
            })).toEqual({
                context: {
                    prop2: null
                },
                json: {
                    type: 'text',
                    prop: null,
                    prop2: null
                }
            });

            expect(error.mock.calls).toHaveLength(0);
        });
    });
});
