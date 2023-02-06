import {Row} from '@yandex-taxi/callcenter-staff/blocks/grid';
import {
    SessionDirection,
    SessionStatus,
    useAnswerCall,
    useEndCall,
    useSession,
    useSessionSelector,
} from '@yandex-taxi/cc-jssip-hooks';
import Button from 'amber-blocks/button';
import {RTCSessionEvent} from 'jssip/lib/UA';
import React, {useEffect} from 'react';

import {ANSWER_CALL_OPTIONS} from '../../consts';

// TODO унести в библиотеку
const toProps = ({session}: RTCSessionEvent) => ({
    phone: session.remote_identity.uri.user,
    queue: session.remote_identity.display_name,
});

// Обработка звонка
const Session = () => {
    const {
        status: sessionStatus,
        direction,
    } = useSession();

    const {
        phone,
        queue,
    } = useSessionSelector(toProps);

    const answerCall = useAnswerCall();
    const endCall = useEndCall();

    useEffect(() => {
        if (sessionStatus) {
            window.parent.postMessage(JSON.stringify({
                type: 'session_status_change',
                payload: {
                    sessionStatus,
                    phone,
                    queue,
                },
            }), '*');
        }
    }, [sessionStatus, phone, queue]);

    return (
        <>
            {sessionStatus === SessionStatus.STARTING && direction === SessionDirection.INCOMING && (
                <>
                    <Row>Входящий вызов</Row>
                    <Row>{`Очередь: ${queue}`}</Row>
                    <Row>{`Номер: ${phone}`}</Row>
                    <Row>
                        <Button onClick={() => answerCall(ANSWER_CALL_OPTIONS)}>Ответить</Button>
                    </Row>
                </>
            )}
            {sessionStatus === SessionStatus.ACTIVE && (
                <>
                    <Row>Вы сейчас разговариваете</Row>
                    <Row>{`Очередь: ${queue}`}</Row>
                    <Row>{`Номер: ${phone}`}</Row>
                    <Row>
                        <Button onClick={() => endCall()}>
                            Закончить вызов
                        </Button>
                    </Row>
                </>
            )}
        </>
    );
};

export default Session;
