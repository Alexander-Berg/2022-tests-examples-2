#!/opt/nodejs/6/bin/node

'use strict';

const XivaWSWorker = require('../server/XivaWSWorker').XivaWSWorker;
const config = require('./config.test');
const tools = require('../server/tools');
const clientPort = 7001;
const assert = require('chai').assert;

config.log.write_to_file = false;

let worker = new XivaWSWorker({ listen: clientPort, config: config });

var SockJSC = require('sockjs-client');
var client = new SockJSC("http://localhost:" + clientPort +"/xiva");
var client2 = new SockJSC("http://localhost:" + clientPort +"/xiva");
var client3 = new SockJSC("http://localhost:" + clientPort +"/xiva");

setTimeout( function(){
    console.log('Execution time limit 10 sec');
    process.exit();
}, 5000 );

client.onmessage = function (msg) {
        // received some data
        console.log('sockjs message', msg);
};
client.onerror =  function (e) {
        // something went wrong
        console.log('sockjs error', e);
    };



  //client.send("Have some text you mighty SockJS server!");


function answer_on_message( client, message ){
    client.send( JSON.stringify( message ))
    return new Promise( (result) => {
        client.onmessage  = function( answer ){
            console.log('SockJs client get:', answer.data);
            result( JSON.parse(answer.data) );
        }
        setTimeout( function(){
            result( null );
        }, 1000);
    })
}



new Promise( result => {
     client.onopen = function () {
        // connection is established
        console.log('sock js client connected');
        result(1);
    };
})
.then( result => {
    assert(1, "client connected");
    return answer_on_message( client, { ping : 1 } );
})
.then( result => {
    assert( result && result.pong , 'pong');
    return answer_on_message( client, { subscribe: ['stream_channel_1', 'channel2_1', 'channel_3']} );
}).then( result => {
    assert( result.ok , "subscribed" );
    return answer_on_message( client, { emoji: 'smile', ch: 'stream_channel_1'} );
}).then( result => {
    //console.log('ANSWER:' ,result);
    assert( result.ok , "emoji registred" );

    assert( worker.clientPool );
    assert( worker.clientPool.length );
    console.log('Pool Size:', worker.clientPool.size() );
    assert( worker.clientPool.size() == 3, " 3 clients");

    for( let id in worker.clientPool.client ){
        console.info('Found client id', id);
        worker.dropClient( id );

        break;
    }

    //collection
    assert.equal( worker.clientPool.size(), 2, " 2 clients");
    console.log('----- collect 1 ');
    worker.collectClients();
    assert.equal( worker.clientPool.size(), 2, " 2 clients");
    assert.equal(worker.clientPool.length, 2 , '2 clients');
    for( let id in worker.clientPool.client ){
        let client = worker.clientPool.client[id]
        //non real
        client.socket._session.ws = null;
        break;
    }

    console.log('----- collect 2 ');
    worker.collectClients();
    assert.equal( worker.clientPool.size() , 1, " 1 clients");
    assert.equal(worker.clientPool.length  , 1 , '1 clients');

    console.log('----- collect 3, by timeout ');
    worker.collectClients( 10 );
    assert.equal( worker.clientPool.size() , 0, " 0 clients");
    assert.equal(worker.clientPool.length  , 0 , 'zerro clients');

    console.log('done');
    process.exit();
});

//todo drop connection
//cleanup connections

