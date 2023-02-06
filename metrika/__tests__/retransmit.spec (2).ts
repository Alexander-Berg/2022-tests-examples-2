import * as chai from 'chai';
import * as sinon from 'sinon';
import * as senderWatch from '@src/sender/watch';
import * as senderWebvisor from '@private/src/sender/webvisor';
import { useRetransmitSender } from '../retransmit';

describe('sender / retransmit', () => {
    const webvisorSenderStub = sinon.stub();
    const watchSenderStub = sinon.stub();
    let getWebvisorSenderStub: sinon.SinonStub;
    let getWatchSenderStub: sinon.SinonStub;

    beforeEach(() => {
        getWebvisorSenderStub = sinon
            .stub(senderWebvisor, 'useSenderWebvisor')
            .returns(webvisorSenderStub);
        getWatchSenderStub = sinon
            .stub(senderWatch, 'useSenderWatch')
            .returns(watchSenderStub);
    });

    afterEach(() => {
        watchSenderStub.resetHistory();
        webvisorSenderStub.resetHistory();
        getWebvisorSenderStub.restore();
        getWatchSenderStub.restore();
    });

    it('calls webvisor sender when vw-type is provided', () => {
        const sender = useRetransmitSender({} as any, [], []);
        const counterOptions: any = {};
        const senderOptions: any = {
            debugStack: [],
            urlParams: {
                ['wv-part']: '1',
            },
        };
        sender(senderOptions, counterOptions, senderWebvisor.WEBVISOR_RESOURCE);

        chai.expect(
            webvisorSenderStub.calledWith(senderOptions, counterOptions, '1'),
        ).to.be.true;
    });

    it('calls watch sender by default', () => {
        const sender = useRetransmitSender({} as any, [], []);
        const counterOptions: any = {};
        const senderOptions: any = {
            debugStack: [],
            urlParams: {},
        };
        sender(senderOptions, counterOptions);

        chai.expect(watchSenderStub.calledWith(senderOptions, counterOptions))
            .to.be.true;
    });
});
