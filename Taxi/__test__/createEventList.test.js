import {EVENT_TYPE} from '@yandex-taxi/omnichat/src/services/task/consts';
import km from 'keymirror';
import {createEventsList, prepareEvents} from 'omnichat/components/chat/createEventList';

let events1 = null;
let events2 = null;
let events3 = null;
let events4 = null;
let events5 = null;
let events6 = null;
let events7 = null;
let events8 = null;
let events9 = null;

const EVENT = km({
    ACTION: null,
    ACTIONS: null,
    EVENT: null
});

function createEvent(type) {
    if (type === EVENT_TYPE.ACTION) {
        return EVENT.ACTION;
    }

    return EVENT.EVENT;
}

function createActions(actions) {
    return actions;
}

const mapPreparedResult = event =>
    Array.isArray(event) ? event.map(e => e.type) : event.type === EVENT_TYPE.MESSAGE ? EVENT.EVENT : event.type;

describe('function test', () => {
    beforeAll(() => {
        events1 = [{type: EVENT_TYPE.ACTION}, {type: EVENT_TYPE.ACTION}, {type: EVENT_TYPE.ACTION}];
        events2 = [{type: EVENT_TYPE.MESSAGE}, {type: EVENT_TYPE.ACTION}, {type: EVENT_TYPE.MESSAGE}];
        events3 = [{type: EVENT_TYPE.MESSAGE}, {type: EVENT_TYPE.MESSAGE}, {type: EVENT_TYPE.ACTION}];
        events4 = [{type: EVENT_TYPE.ACTION}, {type: EVENT_TYPE.ACTION}, {type: EVENT_TYPE.MESSAGE}];
        events5 = [
            {type: EVENT_TYPE.ACTION},
            {type: EVENT_TYPE.ACTION},
            {type: EVENT_TYPE.MESSAGE},
            {type: EVENT_TYPE.ACTION},
            {type: EVENT_TYPE.ACTION},
            {type: EVENT_TYPE.ACTION},
            {type: EVENT_TYPE.MESSAGE},
            {type: EVENT_TYPE.ACTION}
        ];
        events6 = [{type: EVENT_TYPE.ACTION}];
        events7 = [{type: EVENT_TYPE.ACTION}, {type: EVENT_TYPE.ACTION}];
        events8 = [{type: EVENT_TYPE.MESSAGE}];
        events9 = [];
    });

    const funcResult1 = [[EVENT.ACTION, EVENT.ACTION, EVENT.ACTION]];
    it('test1', () => {
        expect(createEventsList(events1, createEvent, createActions)).toEqual(funcResult1);
    });
    it('test1.1', () => {
        expect(prepareEvents(events1).map(mapPreparedResult)).toEqual(funcResult1);
    });

    const funcResult2 = [EVENT.EVENT, [EVENT.ACTION], EVENT.EVENT];
    it('test2', () => {
        expect(createEventsList(events2, createEvent, createActions)).toEqual(funcResult2);
    });
    it('test2.1', () => {
        expect(prepareEvents(events2).map(mapPreparedResult)).toEqual(funcResult2);
    });

    const funcResult3 = [EVENT.EVENT, EVENT.EVENT, [EVENT.ACTION]];
    it('test3', () => {
        expect(createEventsList(events3, createEvent, createActions)).toEqual(funcResult3);
    });
    it('test3.1', () => {
        expect(prepareEvents(events3).map(mapPreparedResult)).toEqual(funcResult3);
    });

    const funcResult4 = [[EVENT.ACTION, EVENT.ACTION], EVENT.EVENT];
    it('test4', () => {
        expect(createEventsList(events4, createEvent, createActions)).toEqual(funcResult4);
    });
    it('test4.1', () => {
        expect(prepareEvents(events4).map(mapPreparedResult)).toEqual(funcResult4);
    });

    const funcResult5 = [
        [EVENT.ACTION, EVENT.ACTION],
        EVENT.EVENT,
        [EVENT.ACTION, EVENT.ACTION, EVENT.ACTION],
        EVENT.EVENT,
        [EVENT.ACTION]
    ];
    it('test5', () => {
        expect(createEventsList(events5, createEvent, createActions)).toEqual(funcResult5);
    });
    it('test5.1', () => {
        expect(prepareEvents(events5).map(mapPreparedResult)).toEqual(funcResult5);
    });

    const funcResult6 = [[EVENT.ACTION]];
    it('test6', () => {
        expect(createEventsList(events6, createEvent, createActions)).toEqual(funcResult6);
    });
    it('test6.1', () => {
        expect(prepareEvents(events6).map(mapPreparedResult)).toEqual(funcResult6);
    });

    const funcResult7 = [[EVENT.ACTION, EVENT.ACTION]];
    it('test7', () => {
        expect(createEventsList(events7, createEvent, createActions)).toEqual(funcResult7);
    });
    it('test7.1', () => {
        expect(prepareEvents(events7).map(mapPreparedResult)).toEqual(funcResult7);
    });

    const funcResult8 = [EVENT.EVENT];
    it('test8', () => {
        expect(createEventsList(events8, createEvent, createActions)).toEqual(funcResult8);
    });
    it('test8.1', () => {
        expect(prepareEvents(events8).map(mapPreparedResult)).toEqual(funcResult8);
    });

    const funcResult9 = [];
    it('test9', () => {
        expect(createEventsList(events9, createEvent, createActions)).toEqual(funcResult9);
    });
    it('test9.1', () => {
        expect(prepareEvents(events9).map(mapPreparedResult)).toEqual(funcResult9);
    });
});
