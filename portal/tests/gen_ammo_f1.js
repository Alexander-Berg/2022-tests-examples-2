#!/opt/nodejs/12/bin/node
/* eslint no-console: 0 */
'use strict';
const fs = require('fs');
const got = require('got');
const _ = require('lodash');
const util = require('util');
const nginxline = /(.*?) - \[.*] ".*?" "(.*?) (.*?)" [\d ]+ "(.*?)" "(.*?)" ".*?" ".*?" "(.*?)"/;
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

let source = fs.readFileSync('./tune.ammo');
source = source.toString().split('\n');

function go(line) {
    let components = nginxline.exec(line);
    if (components) {
        let res = {
            ip: components[1],
            method: components[2],
            location: components[3],
            referrer: components[4],
            useragent: components[5],
            cookies: components[6]
        };
        send_request(res.ip, res.useragent, res.cookies);
    }
}


function requester() {
    if (source.length > 0) {
        let line = source.pop();
        go(line);
        setTimeout(requester, 100);
    }
}
requester();

function send_request(ip, user_agent, cookies) {
    got('https://l7test.yandex.ru/l7tune/api/v1/show_me_the_headers', {
        headers: {
            'host': 'tune-v54d3.wdevx.yandex.ru',
            'X-Forwarded-For-Y': ip,
            'X-Forwarded-For': ip,
            'user-agent': user_agent,
            'cookie': cookies
        }
    })
        .then((res) => console.log(generate_ammo(ip, res.body)))
        .catch((error) => console.log('error:', error));
}

// const template = "GET /l7tune%s HTTP/1.0\r\n" +      // для dev-инстанса
const template = 'GET /tune%s HTTP/1.0\r\n' + // для rc
    // "Host: l7test.yandex.ru\r\n" +
    '%s' + // Место под заголовки
    '\r\n\r\n';
const locations = [
    '/',
    '/places',
    '/search',
    '/geo',
    '/lang',
    '/adv'
];

function generate_ammo(ip, headers) {
    headers = JSON.parse(headers);
    headers = _.map(headers, (value, key) => key + ': ' + value).join('\r\n');
    let location = locations[parseInt(Math.random() * locations.length)];
    let ammo = util.format(template, location, headers);

    return util.format('%d %s\n%s', ammo.length, '', ammo);
}
