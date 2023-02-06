const chai = require('chai');
const e2eUtils = require('../../utils/index.js');
const { findNodeWithAttribute, baseUrl, clearBrowser } = require('./utils');

describe('webvisor2', function () {
    const counterId = 239123;

    const checkMouseData = function (browser, isProto) {
        return browser
            .url(`${baseUrl}mouse.hbs?${isProto ? '' : '_ym_debug=1'}`)
            .getText('h1')
            .then((innerText) => {
                const text = innerText;
                chai.expect(text).to.be.equal('Mouse page');
            })
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        if (options.isProto) {
                            document.cookie = '_ym_debug=""';
                        }
                        window.req = [];
                        serverHelpers.onRequest(function (request) {
                            if (request.url.match(/webvisor\//)) {
                                window.req.push(request);
                            }
                        });
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });
                        done();
                    },
                    counterId,
                    isProto,
                }),
            )
            .pause(1000)
            .moveToObject('#hoverTarget')
            .pause(100)
            .moveToObject('#clickTarget')
            .pause(100)
            .click('#clickTarget')
            .pause(4000)
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        done(window.req);
                    },
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then((visorData) => {
                const page = visorData.find((event) => event.type === 'page');
                const hoverTarget = findNodeWithAttribute(page, 'hoverTarget');
                const clickTarget = findNodeWithAttribute(page, 'clickTarget');

                const events = visorData.filter(
                    (event) =>
                        event.type === 'event' &&
                        event.data.type.startsWith('mouse'),
                );
                const hoverEvents = events.filter(
                    (event) => event.data.target === hoverTarget.id,
                );
                const moveToHover = hoverEvents.shift();
                const moveFromHover = hoverEvents.pop();

                const hoverPosition = moveToHover.data.meta;
                chai.expect(hoverPosition.y, 'hover to y').to.be.above(200);
                chai.expect(hoverPosition.x, 'hover to x').to.be.above(50);
                chai.expect(
                    moveFromHover.data.meta,
                    'hover from y',
                ).to.be.deep.equal(hoverPosition);

                const moveToClick = events.find(
                    (event) =>
                        event.data.target === clickTarget.id &&
                        event.data.type === 'mousemove',
                );
                const mouseDown = events.find(
                    (event) =>
                        event.data.target === clickTarget.id &&
                        event.data.type === 'mousedown',
                );
                const mouseUp = events.find(
                    (event) =>
                        event.data.target === clickTarget.id &&
                        event.data.type === 'mouseup',
                );

                const clickPosition = moveToClick.data.meta;
                chai.expect(clickPosition.x, 'click x').to.be.above(200);
                chai.expect(clickPosition.y, 'click y').to.be.above(500);

                chai.expect(
                    mouseUp.data.meta,
                    'mousedown position',
                ).to.be.deep.equal(clickPosition);
                chai.expect(
                    mouseDown.data.meta,
                    'mouseup position',
                ).to.be.deep.equal(clickPosition);

                let sequenceIsCorrect = true;
                [moveToHover, moveFromHover, moveToClick, mouseDown, mouseUp]
                    .map((e) => e.stamp)
                    .reduce((prevStamp, nextStamp) => {
                        console.log(prevStamp, nextStamp);
                        sequenceIsCorrect =
                            sequenceIsCorrect && prevStamp <= nextStamp;
                        return nextStamp;
                    }, 0);

                chai.assert(
                    sequenceIsCorrect,
                    'events are in the correct order',
                );
            });
    };

    beforeEach(function () {
        return clearBrowser(this.browser);
    });

    it('records mouse (proto)', function () {
        return checkMouseData(this.browser, true);
    });

    it('records mouse (json)', function () {
        return checkMouseData(this.browser, false);
    });
});
