// import * as chai from 'chai';
// import { yandexNamespace, metrikaNamespace } from '@src/storage/global';
// import { mix } from '@src/utils/object';
// import { CounterOptions } from '@src/utils/counterOptions';
// import { dateMock } from '@src/utils/time/__tests__/time.spec';
// import { HID_NAME } from '@src/middleware/watchSyncFlags/hid';
// import { randomMock } from '@src/utils/number/__tests__/number.spec';
// import { eventMock } from '@src/utils/events/__tests__/events.spec';
// import { firstArg } from '@src/utils/function';
// import {
//     INIT_MESSAGE_CHILD,
//     NAME_SPACE,
//     SPLITER,
//     OUT_DIRECTION,
//     MessageData,
//     IFRAME_MESSAGE_TYPE,
// } from '@src/utils/iframeConnector';
// import { errorLogger } from '@src/utils/errorLogger';
// import { iframeSender } from '../iframeSender';
// import { emiterMock } from '../../events/__tests__/emitter.spec';

// export const iframeSenderMock = <T>() => {
//     return {
//         /* eslint-disable @typescript-eslint/no-unused-vars */
//         emitter: emiterMock<T>(),
//         sendToIframe: (c: Window, m: MessageData) => Promise.resolve(1),
//         sendToChildren: (m: MessageData) =>
//             Promise.resolve({ [IFRAME_MESSAGE_TYPE]: '' }),
//         sendToParents: (m: MessageData) =>
//             Promise.resolve({ [IFRAME_MESSAGE_TYPE]: '' }),
//         /* eslint-enable @typescript-eslint/no-unused-vars */
//     };
// };

// describe('iframeSender', () => {
//     const testTime = 1002102113;
//     const dateInfo = {
//         now: testTime,
//         ns: 1010212,
//     };
//     const testHid = 'testHid';
//     const counterOptions: CounterOptions = {
//         id: 101221020,
//         counterType: '0',
//     };

//     const iframeCounterOpt = { id: counterOptions.id + 10, counterType: '1' };
//     const win = (
//         messageTrigger: (cb: (event: MessageEvent) => void) => void,
//         iframeCtx: any = {},
//         winPostMessage: (data: string, origin: string) => any = firstArg,
//         parentCtx: any = {},
//     ) => {
//         return mix(
//             dateMock(testTime, dateInfo),
//             randomMock(),
//             eventMock((name: string, callback) => {
//                 if (name === 'message') {
//                     messageTrigger(callback);
//                 }
//             }),
//             {
//                 throwErr: errorLogger,
//                 name: 'iframeSender',
//                 top: parentCtx,
//                 parent: parentCtx,
//                 JSON,
//                 setTimeout: setTimeout.bind(window),
//                 clearTimeout: clearTimeout.bind(window),
//                 [yandexNamespace]: {
//                     [metrikaNamespace]: {
//                         [HID_NAME]: testHid,
//                     },
//                 },
//                 postMessage: winPostMessage,
//                 document: {
//                     getElementsByTagName: () => [
//                         {
//                             contentWindow: iframeCtx,
//                         },
//                     ],
//                 },
//             },
//         ) as any as Window;
//     };
//     it.skip('await for messages', (done) => {
//         let sendMessage: ((e: MessageEvent) => void) | null = null;
//         const dateKey = 101010;
//         const rnKey = 42;
//         const testEvent = 'testEvent';
//         const iframeTestHid = `${testHid}iframe`;
//         const newWindow = win(
//             () => {},
//             {},
//             (message: string) => {
//                 const parsedMessage = JSON.parse(message);
//                 const [, date, rnIn, dir] =
//                     parsedMessage[NAME_SPACE].split(SPLITER);
//                 if (parsedMessage.data.type !== testEvent) {
//                     return;
//                 }
//                 chai.expect(parsedMessage.data.toCounter).to.be.equal(
//                     `${iframeCounterOpt.id}`,
//                 );
//                 chai.expect(dir).to.be.equal(`${OUT_DIRECTION}`);
//                 setTimeout(() => {
//                     (sendMessage as any)({
//                         source: newWindow,
//                         data: JSON.stringify({
//                             data: [
//                                 {
//                                     counterId: iframeCounterOpt.id,
//                                     hid: iframeTestHid,
//                                 },
//                             ],
//                             [NAME_SPACE]: [
//                                 NAME_SPACE,
//                                 date,
//                                 rnIn,
//                                 parsedMessage.data.counterId,
//                             ].join(SPLITER),
//                         }),
//                     });
//                 }, 0);
//             },
//         );
//         const winInfo = win(
//             (sendMessageInfo) => {
//                 sendMessage = sendMessageInfo;
//             },
//             undefined,
//             undefined,
//             newWindow,
//         );
//         const iframeController = iframeSender(winInfo, counterOptions);
//         if (!iframeController || !sendMessage) {
//             done('empty iframe controler');
//             return;
//         }
//         mix(winInfo, randomMock(0.99));
//         dateInfo.now += 10;
//         iframeController
//             .sendToParents({
//                 [IFRAME_MESSAGE_TYPE]: testEvent,
//             })
//             .then((info: any) => {
//                 chai.expect(info.counterId).to.be.equal(iframeCounterOpt.id);
//                 chai.expect(info.hid).to.be.equal(iframeTestHid);
//                 done();
//             });
//         (sendMessage as any)({
//             source: newWindow,
//             data: JSON.stringify({
//                 data: {
//                     type: INIT_MESSAGE_CHILD,
//                     counterId: iframeCounterOpt.id,
//                     hid: testHid,
//                 },
//                 [NAME_SPACE]: [NAME_SPACE, dateKey, rnKey, OUT_DIRECTION].join(
//                     SPLITER,
//                 ),
//             }),
//         });
//     });
// });
