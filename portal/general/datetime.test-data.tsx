import { execView } from '@lib/views/execView';

const req = {
    HdReason: 'Причина',
    JSTimestamp: 'February 12, 2021, 22:04:26',
    Local: {
        hour: '22',
        min: '04'
    },
    Locale: 'ru',
    Topnews: {
        BigDay: '12',
        BigMonth: 'февраля',
        BigWday: 'пятница',
        LocalMonth: '02'
    },
    MordaZone: 'ru'
};

// Тест мигает, если фликер спрятан. Поэтому показываем ":" всегда в тесте
const styles = <style>
    {`
    .datetime__flicker {
        opacity: 1 !important;
    }
`}
               </style>;

export function simple() {
    return [
        styles,
        execView('Datetime', {}, req)
    ].join('');
}

export function timeOnly() {
    return [
        styles,
        execView('Datetime', {
            timeOnly: true
        }, req)
    ].join('');
}

export function isShort() {
    return [
        styles,
        execView('Datetime', {
            isShort: true
        }, req)
    ].join('');
}
