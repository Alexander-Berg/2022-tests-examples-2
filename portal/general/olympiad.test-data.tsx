import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Olympiad } from '@block/olympiad/olympiad.view';
import * as mocks from './mocks';

export function priorityOutOfTop() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Olympiad: mocks.priorityOutOfTop
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
            {execView('Style', {
                content: 'body{width:270px;}'
            })}
            {execView(Olympiad, {}, req)}
            {resources.getHTML('head')}
        </>
    );
}

export function darkTheme() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Skin: 'night',
        Olympiad: mocks.priorityOutOfTop
    });
    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return {
        skin: 'night',
        html: (
            <>
                {execView('Style', {
                    content: 'body{width:270px;background:#666;color:white}body .home-link{color:white}body .text_black_yes{color: #bfbfbf;}body .olympiad{background:#1d1e22}'
                })}
                {execView(Olympiad, {}, req)}
                {resources.getHTML('head')}
            </>
        )
    };
}

export function priorityOutOfTopNoAlert() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Olympiad: mocks.priorityOutOfTopNoAlert
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
            {execView('Style', {
                content: 'body{width:270px;}'
            })}
            {execView(Olympiad, {}, req)}
            {resources.getHTML('head')}
        </>
    );
}

export function priorityThird() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Olympiad: mocks.priorityThird
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
            {execView('Style', {
                content: 'body{width:270px;}'
            })}
            {execView(Olympiad, {}, req)}
            {resources.getHTML('head')}
        </>
    );
}

export function priorityFourth() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Olympiad: mocks.priorityFourth
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
        {execView('Style', {
            content: 'body{width:270px;}'
        })}
        {execView(Olympiad, {}, req)}
        {resources.getHTML('head')}
        </>
    );
}

export function notStarted() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Olympiad: mocks.notStarted
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
        {execView('Style', {
            content: 'body{width:270px;}'
        })}
        {execView(Olympiad, {}, req)}
        {resources.getHTML('head')}
        </>
    );
}

export function alertOnly() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Olympiad: mocks.alertOnly
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
        {execView('Style', {
            content: 'body{width:270px;}'
        })}
        {execView(Olympiad, {}, req)}
        {resources.getHTML('head')}
        </>
    );
}
