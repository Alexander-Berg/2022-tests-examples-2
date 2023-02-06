#!/opt/nodejs/6/bin/node

'use strict';

const config = require('./config.test');
const tools = require('../server/tools');
const cluster = require('cluster');
const assert = require('chai').assert;
const helper = require('./xiva_helper');

config.masterServers = [
    { port: 8000, host: 'localhost'},
    { port: 8005, host: 'localhost'},
    { port: 8010, host: 'localhost'},
//   { port: 8015, host: 'localhost'},
//    { port: 8020, host: 'localhost'},
//    { port: 8025, host: 'localhost'},
];




const XivaNode = require('../server/XivaNode').XivaNode;
const XivaWSWorker = require('../server/XivaWSWorker').XivaWSWorker;

const WORKERS_COUNT = 10;
const NODES_COUNT = 40;
let NODES = []
for( let i = 0; i<NODES_COUNT; i++){
    let node = new XivaNode(
        {
            id : String.fromCharCode( String('A').charCodeAt(0) + i ),
            listen: 8000 + i,
            workerPort: 7000 + i * WORKERS_COUNT,
            workers: WORKERS_COUNT,
            config: config,
        }
    )
    NODES.push(node);
};

let clients = [];
for( let i = 0 ; i < NODES_COUNT * WORKERS_COUNT - 2 ; i++){
    let client = helper.client(3, 7000 + i , function(){ client.senddata( {subscribe: ['stream_146'] })} );
    clients.push(client);
}
let start;
let finish;
let count = 0;
setTimeout(function(){
    start = new Date().getTime();
    let ts = new Date().getTime()/1000;
    for( let i in clients ){
        clients[i].send( JSON.stringify({
            ch: 'stream_146',
            ts: ts,
            emoji : ['smile','sad','crazy','O_o'][ Math.floor( Math.random()*4 ) ],
        }) );
        clients[i].onmessage = function ( msg ){
            let data = JSON.parse(msg.data);
            //console.log(data);
            if( data.emoji ){
                finish = new Date().getTime();
                count++;
            }
        }
    }
}, 3000);

setTimeout( function(){
    console.log('Delivery takern:', finish - start, 'Messages:', count );
    process.exit();
}, 9000 );




