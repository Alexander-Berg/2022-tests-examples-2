global.console = {
    log: jest.fn(),
    error: console.error,
    warn: jest.fn(),
    info: jest.fn(),
    debug: jest.fn(),
};
