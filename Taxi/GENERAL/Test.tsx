import Duration from '@yandex-taxi/callcenter-staff/blocks/duration/Duration';
import {Col, Row} from '@yandex-taxi/callcenter-staff/blocks/grid';
import Input from '@yandex-taxi/callcenter-staff/blocks/input2';
import {
    SessionStatus,
    Status,
    useAnswerCall,
    useEndCall,
    useOutgoingCall,
    useSendDTMF,
    useSession,
    useSessionMute,
    useTelephonyEphemeralAuth,
    useTelephonyLaunch,
    useTelephonyStatus,
    useUserAgent,
} from '@yandex-taxi/cc-jssip-hooks';
import Button from 'amber-blocks/button';
import {DTMF_TRANSPORT} from 'jssip/lib/Constants';
import moment from 'moment';
import React, {useCallback, useEffect, useRef, useState} from 'react';

import {ANSWER_CALL_OPTIONS} from '../../consts';
import DtmfSender from '../sip/layout2/sidebar/dtmf-sender';
import Session from './Session';

// Компонент обертка
const Test = () => {
    // Получаем состояние статуса
    const [{loading, data, error}, setStatus] = useTelephonyStatus();
    const {status: uaStatus} = useUserAgent();
    const {data: authData, loading: authLoading, error: authError} = useTelephonyEphemeralAuth();
    const {loading: launchLoading, data: launchData, error: launchError} = useTelephonyLaunch();
    const {status: sessionStatus, muted, direction} = useSession();
    const [phone, setPhone] = useState('');
    const additionalId = useRef<string>();
    const sendDtmf = useSendDTMF();
    const [{loading: outgoingLoading, error: outgoingError, waitingCallId}, createOutgoing] = useOutgoingCall();

    const handleOutgoing = useCallback(() => {
        createOutgoing(phone);
    }, [phone, createOutgoing]);
    const answerCall = useAnswerCall();
    const endCall = useEndCall();
    const {mute, unmute} = useSessionMute();
    const [startTime, setStartTime] = useState(null);

    useEffect(() => {
        if (sessionStatus === SessionStatus.ACTIVE) {
            setStartTime(moment());

            return () => {
                setStartTime(null);
            };
        }
    }, [sessionStatus]);

    useEffect(() => {
        if (waitingCallId) {
            window.parent.postMessage(JSON.stringify({
                type: 'outbound_created',
                payload: {
                    external_call_id: waitingCallId,
                    ...additionalId.current && {additional_id: additionalId.current},
                },
            }), '*');
            additionalId.current = undefined;
        }
    }, [waitingCallId]);

    useEffect(() => {
        if (outgoingError) {
            additionalId.current = undefined;
        }
    }, [outgoingError]);

    const status = data?.status;

    useEffect(() => {
        if (authError || launchError) {
            window.parent.postMessage(JSON.stringify({
                type: 'telephony_auth_error',
                payload: {
                    message: 'auth_error',
                },
            }), '*');
        }
    }, [authError, launchError]);

    useEffect(() => {
        if (uaStatus) {
            window.parent.postMessage(JSON.stringify({
                type: 'user_agent_status_change',
                payload: {
                    status: uaStatus,
                },
            }), '*');
        }
    }, [uaStatus]);

    useEffect(() => {
        if (status) {
            window.parent.postMessage(JSON.stringify({
                type: 'status_change',
                payload: {
                    status,
                },
            }), '*');
        }
    }, [status]);
    useEffect(() => {
        if (sessionStatus === SessionStatus.WAITING) {
            window.parent.postMessage(JSON.stringify({
                type: 'session_status_change',
                payload: {
                    sessionStatus,
                },
            }), '*');
        }
    }, [sessionStatus]);
    useEffect(() => {
        if (sessionStatus === SessionStatus.ACTIVE) {
            window.parent.postMessage(JSON.stringify({
                type: 'mute_status_change',
                payload: {
                    is_muted: muted,
                },
            }), '*');
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [muted]);

    useEffect(() => {
        const handleMessage = async (e: MessageEvent) => {
            try {
                if (e.data?.type === 'create_outbound_call') {
                    if (status !== Status.CONNECTED) {
                        setStatus({status: Status.CONNECTED});
                    }
                    setPhone(e.data?.payload?.phone);
                    additionalId.current = e.data?.payload?.additional_id;
                    createOutgoing(e.data?.payload?.phone);
                }
                if (e.data?.type === 'send_dtmf') {
                    const {value, options} = e.data?.payload;
                    if (options?.transportType === DTMF_TRANSPORT.RFC2833) {
                        for (let i of value) {
                            sendDtmf(i, options);
                            // Команды по этому стандарту нужно посылать друг за другом с задержкой
                            // Поэтому так
                            // eslint-disable-next-line no-await-in-loop
                            await new Promise(res => setTimeout(res, 1500));
                        }
                        return;
                    }
                    sendDtmf(value, options);
                }
                if (e.data?.type === 'set_status') {
                    const payload = e.data?.payload;
                    if (payload.status) {
                        setStatus(payload);
                    }
                }
                if (e.data?.type === 'answer_call') {
                    answerCall(ANSWER_CALL_OPTIONS);
                }
                if (e.data?.type === 'end_call') {
                    endCall();
                }
                if (e.data?.type === 'mute') {
                    mute();
                }
                if (e.data?.type === 'unmute') {
                    unmute();
                }
            } catch (e) {
                // pass
            }
        };
        window.addEventListener('message', handleMessage);

        return () => {
            window.removeEventListener('message', handleMessage);
        };
    }, [setStatus, sendDtmf, status, createOutgoing, answerCall, endCall, mute, unmute]);

    if (authError || launchError) {
        return <div>Ошибка получения данных для подключения к серверам телефонии</div>;
    }

    if (authLoading || !authData || launchLoading || !launchData) {
        return <div>Загружаем данные</div>;
    }

    const disabled = sessionStatus !== SessionStatus.WAITING || outgoingLoading || !!waitingCallId;

    return (
        <div style={{height: '100vh', background: 'white'}}>
            <Row>{`Ваш логин: ${launchData?.sip_username}`}</Row>
            <Row>{`Ваш текущий статус в телефонии: ${data?.status}`}</Row>
            <Row>{`Ваш текущий статус на регистарах: ${uaStatus}`}</Row>
            <Row gap="s">
                <Col gap="s">
                    <Button disabled={loading || data?.status === Status.CONNECTED} loading={loading} onClick={() => setStatus({status: Status.CONNECTED})}>
                        Выйти на линию
                    </Button>
                </Col>
                <Col gap="s">
                    <Button disabled={loading || data?.status === Status.DISCONNECTED} loading={loading} onClick={() => setStatus({status: Status.DISCONNECTED})}>
                        Уйти с линии
                    </Button>
                </Col>
            </Row>
            {data?.status === Status.CONNECTED && (
                <Row gap="no" valign="center">
                    <Col>
                        <Input
                            disabled={disabled}
                            placeholder="Телефон"
                            theme={'outline'}
                            value={phone}
                            onChange={(v: string) => setPhone(v)}
                        />
                    </Col>
                    <Col>
                        <Button
                            onClick={handleOutgoing}
                            disabled={!phone || disabled}
                            theme="accent"
                        >
                            Вызвать
                        </Button>
                    </Col>
                </Row>
            )}
            {startTime && (
                <Row>
                    <span style={{marginRight: '8px'}}>Время разговора:</span>
                    <Duration diff={0} start={startTime}/>
                </Row>
            )}
            {direction === 'outgoing' && (
                <Row>
                    <DtmfSender theme="outline" dtmfOptions={{transportType: DTMF_TRANSPORT.RFC2833}}/>
                </Row>
            )}
            {outgoingError && <Row>Ошибка при исходящем звонке</Row>}
            {error && <Row>Ошибка статуса</Row>}
            {sessionStatus !== SessionStatus.WAITING && <Session/>}
        </div>
    );
};

export default Test;
