import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Weather } from '@block/weather/weather.view';
import * as mocks from './mocks';

export function simple() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Weather: mocks.simple
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
            {execView('Style', {
                content: 'body{width:270px;}'
            })}
            {execView(Weather, {}, req)}
            {resources.getHTML('head')}
        </>
    );
}

export function nolinks() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {}
        },
        Weather: mocks.nolinks
    });

    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return (
        <>
            {execView('Style', {
                content: 'body{width:270px;}'
            })}
            {execView(Weather, {}, req)}
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
        Weather: mocks.simple
    });
    const resources = new home.Resources('white', req, execView);
    req.resources = resources;

    return {
        skin: 'night',
        html: (
            <>
                {execView('Style', {
                    content: 'body{width:270px;background:#666;color:white}body .home-link{color:white}'
                })}
                {execView(Weather, {}, req)}
                {resources.getHTML('head')}
            </>
        )
    };
}
