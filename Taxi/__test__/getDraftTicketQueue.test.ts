describe('getDraftTicketQueue', () => {
    afterEach(() => {
        jest.resetModules();
    });

    describe('Когда в конфиге описан сервис', () => {
        beforeAll(() => {
            jest.doMock('_pkg/config', () => ({
                lang: 'ru',
                backendConfigs: {
                    TICKET_QUEUES: {
                        serviceName: {
                            __default__: 'serviceName.default',
                            apiPath: 'serviceName.apiPath'
                        }
                    }
                }
            }));
        });

        it('Возвращает название очереди по имени сервиса и api_path', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            const queueName = getDraftTicketQueue('serviceName', 'apiPath');
            expect(queueName).toBe('serviceName.apiPath');
        });

        it('Возвращает название очереди по-умолчанию по имени сервиса', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            const queueName = getDraftTicketQueue('serviceName', '');
            expect(queueName).toBe('serviceName.default');
        });
    });

    describe('Когда в конфиге описана секция admin', () => {
        beforeAll(() => {
            jest.doMock('_pkg/config', () => ({
                lang: 'ru',
                backendConfigs: {
                    TICKET_QUEUES: {
                        admin: {
                            __default__: 'admin.default',
                            apiPath: 'admin.apiPath'
                        }
                    }
                }
            }));
        });

        it('Возвращает название очереди из секции admin по api_path', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            const queueName = getDraftTicketQueue('serviceName', 'apiPath');
            expect(queueName).toBe('admin.apiPath');
        });

        it('Возвращает название очереди по-умолчанию из секции admin', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            const queueName = getDraftTicketQueue('serviceName', '');
            expect(queueName).toBe('admin.default');
        });
    });

    describe('Когда в конфиге описана секция __default__', () => {
        beforeAll(() => {
            jest.mock('_pkg/config', () => ({
                lang: 'ru',
                backendConfigs: {
                    TICKET_QUEUES: {
                        __default__: {
                            __default__: '__default__.default',
                            apiPath: '__default__.apiPath'
                        }
                    }
                }
            }));
        });

        it('Возвращает название очереди из секции __default__ по api_path', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            const queueName = getDraftTicketQueue('serviceName', 'apiPath');
            expect(queueName).toBe('__default__.apiPath');
        });

        it('Возвращает название очереди по-умолчанию из секции __default__', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            const queueName = getDraftTicketQueue('serviceName', '');
            expect(queueName).toBe('__default__.default');
        });
    });

    describe('Когда в конфиге не описана секция admin, но есть сервис и __default__', () => {
        beforeAll(() => {
            jest.doMock('_pkg/config', () => ({
                lang: 'ru',
                backendConfigs: {
                    TICKET_QUEUES: {
                        serviceName: {
                            __default__: 'service.__default__',
                            serviceApiPath: 'service.apiPath'
                        },
                        __default__: {
                            __default__: '__default__.__default__',
                            defaultApiPath: '__default__.apiPath'
                        }
                    }
                }
            }));
        });

        it('Возвращает название очереди в правильном приоритете', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            expect(getDraftTicketQueue('serviceName', 'serviceApiPath')).toBe('service.apiPath');
            expect(getDraftTicketQueue('serviceName', '')).toBe('service.__default__');
            expect(getDraftTicketQueue('', 'defaultApiPath')).toBe('__default__.apiPath');
            expect(getDraftTicketQueue('', '')).toBe('__default__.__default__');
        });
    });

    describe('Когда в конфиге не описана секция сервиса, но есть admin и __default__', () => {
        beforeAll(() => {
            jest.doMock('_pkg/config', () => ({
                lang: 'ru',
                backendConfigs: {
                    TICKET_QUEUES: {
                        admin: {
                            __default__: 'admin.__default__',
                            adminApiPath: 'admin.apiPath'
                        },
                        __default__: {
                            __default__: '__default__.default',
                            defaultApiPath: '__default__.apiPath'
                        }
                    }
                }
            }));
        });

        it('Возвращает название очереди в правильном приоритете', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            expect(getDraftTicketQueue('serviceName', 'adminApiPath')).toBe('admin.apiPath');
            expect(getDraftTicketQueue('serviceName', '')).toBe('admin.__default__');
            expect(getDraftTicketQueue('', 'adminApiPath')).toBe('admin.apiPath');
            expect(getDraftTicketQueue('', '')).toBe('admin.__default__');
        });
    });

    describe('Когда в конфиге описаны все возможные секции', () => {
        beforeAll(() => {
            jest.doMock('_pkg/config', () => ({
                lang: 'ru',
                backendConfigs: {
                    TICKET_QUEUES: {
                        serviceName: {
                            __default__: 'service.__default__',
                            serviceApiPath: 'service.apiPath'
                        },
                        admin: {
                            __default__: 'admin.__default__',
                            adminApiPath: 'admin.apiPath'
                        },
                        __default__: {
                            __default__: '__default__.default',
                            defaultApiPath: '__default__.apiPath'
                        }
                    }
                }
            }));
        });

        it('Возвращает название очереди в правильном приоритете', async () => {
            const {getDraftTicketQueue} = await import('../utils');

            expect(getDraftTicketQueue('serviceName', 'serviceApiPath')).toBe('service.apiPath');
            expect(getDraftTicketQueue('serviceName', '')).toBe('service.__default__');
            expect(getDraftTicketQueue('', 'adminApiPath')).toBe('admin.apiPath');
            expect(getDraftTicketQueue('', '')).toBe('admin.__default__');
        });
    });

    describe('Когда в конфиге пусто', () => {
        beforeAll(() => {
            jest.mock('_pkg/config', () => ({
                lang: 'ru',
                backendConfigs: {
                    TICKET_QUEUES: {}
                }
            }));
        });

        it('Возвращает название очереди по-умолчанию', async () => {
            const {getDraftTicketQueue, DEFAULT_DRAFT_TICKET_QUEUE} = await import('../utils');

            const queueName = getDraftTicketQueue('serviceName', 'apiPath');
            expect(queueName).toBe(DEFAULT_DRAFT_TICKET_QUEUE);
        });
    });
});
