const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

const findAllEvents = (data, eventName) => {
    if (!data || !Array.isArray(data)) {
        return [];
    }

    return data.filter((item) => {
        return (
            item && item.data && item.data.kind && item.data.kind === eventName
        );
    });
};

const getDataByRequests = (requests) => {
    return requests.reduce((acc, request) => {
        return [...acc, ...request.body];
    }, []);
};

const getRequestsCollector = (browser) =>
    e2eUtils.provideServerHelpers(browser, {
        cb(serverHelpers, options, done) {
            window.requests = [];
            serverHelpers.onRequest(function (request) {
                window.requests.push(request);
            }, options.regexp.webvisorRequestRegEx);
            done(true);
        },
    });

const getRequestsFlusher = (browser) =>
    e2eUtils.provideServerHelpers(browser, {
        cb(serverHelpers, options, done) {
            setTimeout(() => {
                done(window.requests);
            }, 3000);
        },
    });
/**
 * Как это работает?
 * Есть две страницы socketOff и socketOn.
 * Нужно зайти на страницу socketOff и выполнить все нужные действия.
 * Они будут записываться в буффер вебвизора.
 * Далее нужно сделать переход на страницу socketOn,
 * все что было в буффере вебвизора моментально зафлашится (иначе ждать таймаут 30 сек).
 * Отправится запрос с wv-data и сохранится в буффере сокета на сервере,
 * так как сокет соединение не установлено.
 * Далее страница socketOn загрузится, сокет заинитится и буффер сокета зафлашится,
 * мы получим все события с предыдущей страницы на текущей.
 * Далее нужно их собрать и проверить.
 */
describe('Formvisor e2e test', function () {
    const baseDir = 'test/formvisor';
    const socketOff = `${baseDir}/formvisor-socket-off.hbs`;
    const socketOn = `${baseDir}/formvisor-socket-on.hbs`;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(3000);
    });

    it('should be single MouseClickEvent', function () {
        return this.browser
            .url(socketOff)
            .pause(500)
            .click('.title')
            .pause(500)
            .url(socketOn)
            .then(getRequestsCollector(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(getRequestsFlusher(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                requests
                    .map(e2eUtils.getRequestParams)
                    .forEach(({ brInfo }) => {
                        chai.expect(brInfo.rqn).to.be.undefined;
                    });
                const data = getDataByRequests(requests);
                const clicks = findAllEvents(data, 'MouseClickEvent');
                chai.expect(clicks.length).to.equal(1);
            });
    });

    it('should be single FieldFocusEvent and MouseClickEvent', function () {
        return this.browser
            .url(socketOff)
            .pause(500)
            .click('.surname-input')
            .pause(500)
            .url(socketOn)
            .then(getRequestsCollector(this.browser))
            .then(getRequestsFlusher(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const data = getDataByRequests(requests);

                const clicks = findAllEvents(data, 'MouseClickEvent');
                const fieldFocuses = findAllEvents(data, 'FieldFocusEvent');

                chai.expect(clicks.length, 'clicks.length').to.equal(1);
                chai.expect(
                    fieldFocuses.length,
                    'fieldFocuses.length',
                ).to.equal(1);
            });
    });

    it('should be FieldChangeEvent', function () {
        const text = 'hello world';
        return this.browser
            .url(socketOff)
            .pause(500)
            .setValue('.surname-input', text)
            .pause(500)
            .click('.title')
            .pause(500)
            .url(socketOn)
            .then(getRequestsCollector(this.browser))
            .then(getRequestsFlusher(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const data = getDataByRequests(requests);

                // TODO: keyDownEvents ведут себя непредсказуемо локально и на сервере (разобраться почему)
                // const keyDownEvents = findAllEvents(data, 'KeyDownEvent');
                // chai.expect(keyDownEvents.length).to.equal(11);

                const clicks = findAllEvents(data, 'MouseClickEvent');
                const fieldFocuses = findAllEvents(data, 'FieldFocusEvent');
                const fieldChanges = findAllEvents(data, 'FieldChangeEvent');
                const fieldBlurs = findAllEvents(data, 'FieldBlurEvent');

                chai.expect(clicks.length, 'clicks.length').to.equal(1);
                chai.expect(
                    fieldFocuses.length,
                    'fieldFocuses.length',
                ).to.equal(1);
                chai.expect(
                    fieldChanges.length,
                    'fieldChanges.length',
                ).to.equal(1);
                chai.expect(
                    fieldChanges[0].data.value,
                    'fieldChanges[0].data.value',
                ).to.equal(text);
                chai.expect(fieldBlurs.length, 'fieldBlurs.length').to.equal(1);
            });
    });

    it('should be submit', function () {
        const name = 'Ivan';
        const surname = 'Pupkin';
        return this.browser
            .url(socketOff)
            .pause(500)
            .setValue('.name-input', name)
            .pause(500)
            .setValue('.surname-input', surname)
            .pause(500)
            .click('.submit-button')
            .pause(500)
            .then(getRequestsCollector(this.browser))
            .then(getRequestsFlusher(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const data = getDataByRequests(requests);

                const clicks = findAllEvents(data, 'MouseClickEvent');
                const fieldFocuses = findAllEvents(data, 'FieldFocusEvent');
                const fieldBlurs = findAllEvents(data, 'FieldBlurEvent');
                const submitEvents = findAllEvents(data, 'SubmitEvent');
                const fieldChanges = findAllEvents(data, 'FieldChangeEvent');
                const eof = findAllEvents(data, 'EOF');

                chai.expect(clicks.length, 'clicks.length').to.equal(1);
                chai.expect(
                    fieldFocuses.length,
                    'fieldFocuses.length',
                ).to.equal(3);
                chai.expect(fieldBlurs.length, 'fieldBlurs.length').to.equal(2);
                chai.expect(
                    submitEvents.length,
                    'submitEvents.length',
                ).to.equal(1);
                chai.expect(
                    fieldChanges.length,
                    'fieldChanges.length',
                ).to.equal(2);
                chai.expect(eof.length, 'eof.length').to.greaterThan(0);
            });
    });

    it('should be mousemove', function () {
        return this.browser
            .url(socketOff)
            .pause(500)
            .moveToObject('.title', 0, 0)
            .pause(500)
            .moveToObject('.submit-button', 0, 0)
            .pause(500)
            .url(socketOn)
            .then(getRequestsCollector(this.browser))
            .then(getRequestsFlusher(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const data = getDataByRequests(requests);
                const moves = findAllEvents(data, 'MouseMoveEvent');
                chai.expect(moves.length, 'moves.length').to.greaterThan(1);
            });
    });

    it('should be scroll and local scroll', function () {
        return this.browser
            .url(socketOff)
            .pause(500)
            .moveToObject('.scroll-medium', 0, 0)
            .pause(500)
            .moveToObject('.scroll-bottom', 0, 0)
            .pause(500)
            .url(socketOn)
            .then(getRequestsCollector(this.browser))
            .then(getRequestsFlusher(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const data = getDataByRequests(requests);
                const scrolls = findAllEvents(data, 'ScrollEvent');
                const localScrolls = findAllEvents(data, 'ScrollElementEvent');
                chai.expect(scrolls.length, 'scrolls.length').to.greaterThan(0);
                chai.expect(
                    localScrolls.length,
                    'localScrolls.length',
                ).to.greaterThan(0);
            });
    });

    it('should be resize', function () {
        return this.browser
            .url(socketOff)
            .pause(500)
            .setViewportSize({
                width: 500,
                height: 500,
            })
            .pause(500)
            .url(socketOn)
            .then(getRequestsCollector(this.browser))
            .then(getRequestsFlusher(this.browser))
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const data = getDataByRequests(requests);
                const resizes = findAllEvents(data, 'ResizeEvent');
                // Resize при загрузке страницы и setViewportSize (всего 2)
                chai.expect(resizes.length, 'resizes.length').to.greaterThan(0);
            });
    });

    /**
     * TODO:
     * Пока не удалось написать тесты на onMouseWheel, onTouchMove
     * В webdriverio это сделать трудно, возможно лучше проверить это в unit тестах
     */
});
