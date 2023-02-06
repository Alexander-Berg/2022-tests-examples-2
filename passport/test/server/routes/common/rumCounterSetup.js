// const config = require('../../../../configs/current');
// const expect = require('expect.js');
// const sinon = require('sinon');
// const proxyquire = require('proxyquire');
// const RUM_ID = 'ru.1207.auth';
// const REGION_ID = 99;
// const REQUEST_ID = 'x-request-id';
// const REFERRER = 'referrer';
// const EXPERIMENTS_FLAGS = ['exp.1', 'exp.2'];
// const PAGE_ID = '/auth';
// const VERSION = config.version;
// const YANDEXUID = 'yandexuid';
//
// const rumInterface = require('../../../../lib/rum-counter/interface');
// const rumLongTask = require('../../../../lib/rum-counter/longtask');
// const rumIO = require('../../../../lib/rum-counter/io');
// const rumInit = require('../../../../lib/rum-counter/init');
// const rumSend = require('../../../../lib/rum-counter/send');
// const getErrorCounter = require('../../../../lib/rum-counter/error-counter');
// const errorCounterInit = require('../../../../lib/rum-counter/error-counter-init');
//
// describe('rumCounterSetup', () => {
//     let headerSpy = sinon.spy((header) => header);
//     const rumScript = '<rumInterface><rumIO><rumLongTask><rumSend><getErrorCounter><errorCounterInit><rumInit>';
//     const req = {
//         cookies: {
//             yandexuid: YANDEXUID
//         },
//         header: headerSpy,
//         _controller: {
//             getUrl: () => ({
//                 pathname: '/auth'
//             }),
//             getTld: () => 'ru'
//         }
//     };
//     const res = {
//         locals: {
//             regionId: REGION_ID,
//             experiments: {
//                 flags: ['exp.1', 'exp.2'],
//                 boxes: ['exp.1', 'exp.2']
//             }
//         }
//     };
//     const nextSpy = sinon.spy();
//
//     let rumInterfaceStub;
//
//     let rumLongTaskStub;
//
//     let rumIOStub;
//
//     let rumInitStub;
//
//     let rumSendStub;
//
//     let getErrorCounterStub;
//
//     let errorCounterInitStub;
//
//     let rumCounterSetup;
//
//     beforeEach(() => {
//         rumInterfaceStub = sinon.stub(rumInterface, 'getRumInterface').returns('<rumInterface>');
//         rumLongTaskStub = sinon.stub(rumLongTask, 'getRumLongTask').returns('<rumLongTask>');
//         rumIOStub = sinon.stub(rumIO, 'getRumIO').returns('<rumIO>');
//         rumInitStub = sinon.stub(rumInit, 'rumInit').returns('<rumInit>');
//         rumSendStub = sinon.stub(rumSend, 'getRumSend').returns('<rumSend>');
//         getErrorCounterStub = sinon.stub(getErrorCounter, 'getErrorCounter').returns('<getErrorCounter>');
//         errorCounterInitStub = sinon.stub(errorCounterInit, 'errorCounterInit').returns('<errorCounterInit>');
//         rumCounterSetup = proxyquire('../../../../routes/common/rumCounterSetup', {
//             '../../../../lib/rum-counter/interface': {
//                 getRumInterface: rumInterfaceStub
//             },
//             '../../../../lib/rum-counter/longtask': {
//                 getRumLongTask: rumLongTaskStub
//             },
//             '../../../../lib/rum-counter/io': {
//                 getRumIO: rumIOStub
//             },
//             '../../../../lib/rum-counter/init': {
//                 runInit: rumInitStub
//             },
//             '../../../../lib/rum-counter/send': {
//                 getRumSend: rumSendStub
//             },
//             '../../../../lib/rum-counter/error-counter': {
//                 getErrorCounter: getErrorCounterStub
//             },
//             '../../../../lib/rum-counter/error-counter-init': {
//                 errorCounterInit: errorCounterInitStub
//             }
//         });
//     });
//
//     afterEach(() => {
//         rumInterface.getRumInterface.restore();
//         rumLongTask.getRumLongTask.restore();
//         rumIO.getRumIO.restore();
//         rumInit.rumInit.restore();
//         rumSend.getRumSend.restore();
//         getErrorCounter.getErrorCounter.restore();
//         errorCounterInit.errorCounterInit.restore();
//         nextSpy.reset();
//         headerSpy.reset();
//     });
//
//     it('should merge inline scripts with custom configs', () => {
//         const config = {
//             page: PAGE_ID,
//             rumId: RUM_ID,
//             regionId: REGION_ID,
//             requestId: REQUEST_ID,
//             slots: EXPERIMENTS_FLAGS,
//             platform: 'desktop',
//             version: VERSION,
//             experiments: EXPERIMENTS_FLAGS.join(';'),
//             yandexuid: YANDEXUID,
//             referrer: REFERRER
//         };
//
//         rumCounterSetup(req, res, nextSpy);
//
//         expect(res.locals.rumScripts).to.be(rumScript);
//         expect(rumInitStub.calledOnce).to.be.ok();
//         expect(nextSpy.called).to.be.ok();
//         expect(nextSpy.calledOnce).to.be.ok();
//         expect(rumInitStub.calledWith(config)).to.be.ok();
//     });
//
//     it('should merge inline scripts with mobile configs', () => {
//         const config = {
//             page: PAGE_ID,
//             rumId: `${RUM_ID}.touch`,
//             regionId: REGION_ID,
//             requestId: REQUEST_ID,
//             slots: EXPERIMENTS_FLAGS,
//             platform: 'touch',
//             version: VERSION,
//             experiments: EXPERIMENTS_FLAGS.join(';'),
//             yandexuid: YANDEXUID,
//             referrer: REFERRER
//         };
//
//         res.locals.ua = {
//             isMobile: true
//         };
//
//         rumCounterSetup(req, res, nextSpy);
//
//         expect(res.locals.rumScripts).to.be(rumScript);
//         expect(rumInitStub.calledOnce).to.be.ok();
//         expect(nextSpy.called).to.be.ok();
//         expect(nextSpy.calledOnce).to.be.ok();
//         expect(rumInitStub.calledWith(config)).to.be.ok();
//     });
//
//     it('should merge inline scripts with default configs', () => {
//         const config = {
//             page: PAGE_ID,
//             rumId: RUM_ID,
//             platform: 'desktop',
//             version: VERSION,
//             experiments: '',
//             regionId: '',
//             requestId: '',
//             slots: [],
//             yandexuid: YANDEXUID,
//             referrer: ''
//         };
//
//         delete res.locals.ua;
//         delete res.locals.rumScripts;
//         delete res.locals.regionId;
//         delete res.locals.experiments;
//
//         headerSpy = sinon.spy(() => null);
//         req.header = headerSpy;
//
//         rumCounterSetup(req, res, nextSpy);
//
//         expect(res.locals.rumScripts).to.be(rumScript);
//         expect(nextSpy.called).to.be.ok();
//         expect(nextSpy.calledOnce).to.be.ok();
//         expect(rumInitStub.called).to.be.ok();
//         expect(rumInitStub.calledWith(config)).to.be.ok();
//     });
// });
