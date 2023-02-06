import {Col, Row} from '@yandex-taxi/callcenter-staff/blocks/grid';
import {
    SessionStatus,
    Status,
    useSession,
    useTelephonyEphemeralAuth,
    useTelephonyLaunch,
    useTelephonyStatus,
    useUserAgent,
} from '@yandex-taxi/cc-jssip-hooks';
import Button from 'amber-blocks/button';
import React, {useEffect} from 'react';

import Session from './Session';

// Компонент обертка
const Test = () => {
    // Получаем состояние статуса
    const [{loading, data, error}, setStatus] = useTelephonyStatus();
    const {status: uaStatus} = useUserAgent();
    const {data: authData, loading: authLoading, error: authError} = useTelephonyEphemeralAuth();
    const {loading: launchLoading, data: launchData, error: launchError} = useTelephonyLaunch();
    const {status: sessionStatus} = useSession();

    const status = data?.status;

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

    if (authError || launchError) {
        return <div>Ошибка получения данных для подключения к серверам телефонии</div>;
    }

    if (authLoading || !authData || launchLoading || !launchData) {
        return <div>Загружаем данные</div>;
    }

    return (
        <div>
            <Row>
                <h1>Тестирование библиотеки</h1>
            </Row>
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
            {error && <Row>Ошибка статуса</Row>}
            {sessionStatus !== SessionStatus.WAITING && <Session/>}
        </div>
    );
};

export default Test;
