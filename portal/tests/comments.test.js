const {periodicPing} = require('../comments.js');

describe('comments', function () {
    describe('periodicPing', function () {
        const DAY = 24 * 60 * 60 * 1000,
            DELTA = 10 * DAY,
            fakeSt = {
                postComment: function () {}
            },
            fakeComment = {
                createdAt: DELTA / 2,
                text: 'test'
            };
        let postCommentStub,
            pingFunc,
            timer;

        beforeEach(function () {
            postCommentStub = sinon.stub(fakeSt, 'postComment');
            pingFunc = periodicPing(fakeSt, DELTA);
            timer = sinon.useFakeTimers({now: DELTA / 2});
        });

        afterEach(function () {
            sinon.restore();
        });

        it('не постит коммент, если с последнего коммента не прошло delta', async function () {
            for (var i = 0; i < 10; i++) {
                await pingFunc({}, fakeComment, 'test2');
                postCommentStub.should.not.be.called;
                timer.tick(DAY);
            }
        });


        it('не постит коммент, если с создания таска не прошло delta', async function () {
            for (var i = 0; i < 10; i++) {
                await pingFunc(fakeComment, null, 'test2');
                postCommentStub.should.not.be.called;
                timer.tick(DAY);
            }
        });

        it('не постит коммент, если новый коммент пустой', async function () {
            timer.tick(DELTA);
            await pingFunc({}, fakeComment, '');
            postCommentStub.should.not.be.called;
        });

        it('постит коммент, если с последнего коммента прошло > delta', async function () {
            timer.tick(DELTA);
            await pingFunc({}, fakeComment, 'test2');
            postCommentStub.should.be.called;
        });

        describe('флаг forceUpdated', function () {
            it('не постит коммент, если не прошло delta и текст такой же', async function () {
                for (var i = 0; i < 10; i++) {
                    await pingFunc({}, fakeComment, 'test', {forceUpdated: true});
                    postCommentStub.should.not.be.called;
                    timer.tick(DAY);
                }
            });
            it('постит коммент, если не прошло delta, но текст другой', async function () {
                await pingFunc({}, fakeComment, 'qq', {forceUpdated: true});
                postCommentStub.should.be.called;
            });
        });

        it('постит в правильном формате', async function () {
            timer.tick(DELTA);
            await pingFunc({}, fakeComment, 'test2');
            postCommentStub.should.be.deep.calledWith({}, {summonees: [], text: 'test2'});
        });
    });
});