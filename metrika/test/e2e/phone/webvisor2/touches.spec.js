const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

// TODO добавить зумы когда ситуация с бровзерами устанаканится
describe('webvisor2 touches', function () {
    const baseUrl = 'test/webvisor2/';
    const counterId = 123;
    it('Records touches', function () {
        return (
            this.browser
                .timeoutsAsyncScript(6000)
                .url(`${baseUrl}webvisor2-keystroke.hbs`)
                .getText('h1')
                .then((innerText) => {
                    const text = innerText;
                    chai.expect(text).to.be.equal('Keystroke captor test');
                })
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            window.req = [];
                            serverHelpers.collectRequests(
                                2000,
                                (requests) => {
                                    window.req = window.req.concat(requests);
                                    done();
                                },
                                options.regexp.webvisorRequestRegEx,
                            );
                            new Ya.Metrika2({
                                id: options.counterId,
                                webvisor: true,
                            });
                        },
                        counterId,
                    }),
                )
                .pause(1000)
                // http://v4.webdriver.io/api/protocol/actions.html
                // https://discuss.appium.io/t/zoom-in-on-web-browser/19518
                /* 
                TODO  Ожидается что тут будет зум, но его нет так как, ни браузеры ни appium не могут mulitouch в мобильном режиме
                */
                .actions([
                    {
                        type: 'pointer',
                        id: 'finger1',
                        parameters: { pointerType: 'touch' },
                        actions: [
                            {
                                type: 'pointerMove',
                                duration: 0,
                                x: 100,
                                y: 100,
                            },
                            { type: 'pointerDown', button: 0 },
                            { type: 'pause', duration: 500 },
                            {
                                type: 'pointerMove',
                                duration: 200,
                                origin: 'pointer',
                                x: -50,
                                y: 0,
                            },
                            { type: 'pointerUp', button: 0 },
                        ],
                    },
                    {
                        type: 'pointer',
                        id: 'finger2',
                        parameters: { pointerType: 'touch' },
                        actions: [
                            {
                                type: 'pointerMove',
                                duration: 0,
                                x: 110,
                                y: 100,
                            },
                            { type: 'pointerDown', button: 0 },
                            { type: 'pause', duration: 500 },
                            {
                                type: 'pointerMove',
                                duration: 200,
                                origin: 'pointer',
                                x: 50,
                                y: 0,
                            },
                            { type: 'pointerUp', button: 0 },
                        ],
                    },
                ])
                .pause(3000)
                .actions()
                .execute(function () {
                    return {
                        reqs: window.req,
                    };
                })
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: { reqs: requests } }) => {
                    const requestsInfo = requests.map(
                        e2eUtils.getRequestParams,
                    );
                    const bufferData = requestsInfo.reduce((acc, item) => {
                        return acc.concat(item.body);
                    }, []);

                    const touchIds = [];
                    const touchesHash = {};
                    bufferData.forEach((event) => {
                        if (event.type === 'event') {
                            if (
                                event.data &&
                                event.data.meta &&
                                event.data.meta.touches
                            ) {
                                const { stamp } = event;
                                const { touches } = event.data.meta;
                                const { type } = event.data;
                                touches.forEach((touch) => {
                                    const { id } = touch;
                                    touch.stamp = stamp;
                                    touch.type = type;
                                    if (!touchesHash[id]) {
                                        touchIds.push(id);
                                        touchesHash[id] = [touch];
                                    } else {
                                        touchesHash[id].push(touch);
                                    }
                                });
                            }
                        }
                    });

                    chai.expect(touchIds.length).to.equal(2);
                    let foundTouch1 = false;
                    let foundTouch2 = false;

                    const isSomewhatEqual = (a, b) => {
                        return a + 20 >= b && a - 20 <= b;
                    };

                    touchIds.forEach((touchId) => {
                        const [touchStart, touchMove, touchEnd] = touchesHash[
                            touchId
                        ].sort((a, b) => a.stamp - b.stamp);
                        chai.expect(touchStart.type).to.equal('touchstart');
                        chai.expect(touchMove.type).to.equal('touchmove');
                        chai.expect(touchEnd.type).to.equal('touchend');
                        const startStamp = touchStart.stamp;
                        if (touchStart.x === 100) {
                            foundTouch1 = true;
                            chai.expect(touchStart.x).to.equal(100);
                            chai.expect(touchStart.y).to.equal(100);

                            chai.expect(touchMove.x).to.equal(50);
                            chai.expect(touchMove.y).to.equal(100);
                            chai.assert(
                                isSomewhatEqual(
                                    touchMove.stamp,
                                    startStamp + 500,
                                ),
                            );

                            chai.expect(touchEnd.x).to.equal(50);
                            chai.expect(touchEnd.y).to.equal(100);
                            chai.assert(
                                isSomewhatEqual(
                                    touchEnd.stamp,
                                    startStamp + 700,
                                ),
                            );
                        } else {
                            foundTouch2 = true;
                            chai.expect(touchStart.x).to.equal(110);
                            chai.expect(touchStart.y).to.equal(100);

                            chai.expect(touchMove.x).to.equal(160);
                            chai.expect(touchMove.y).to.equal(100);
                            chai.assert(
                                isSomewhatEqual(
                                    touchMove.stamp,
                                    startStamp + 500,
                                ),
                            );

                            chai.expect(touchEnd.x).to.equal(160);
                            chai.expect(touchEnd.y).to.equal(100);
                            chai.assert(
                                isSomewhatEqual(
                                    touchEnd.stamp,
                                    startStamp + 700,
                                ),
                            );
                        }
                    });

                    chai.assert(foundTouch1 && foundTouch2);
                })
        );
    });
});
