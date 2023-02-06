#!/opt/nodejs/6/bin/node

'use strict';

const XivaWSWorker = require('../server/XivaWSWorker').XivaWSWorker;
const config = require('./config.test');
const tools = require('../server/tools');
const clientPort = 7001;
const assert = require('chai').assert;

var SockJSC = require('sockjs-client');

function client( n, port , onReady ){
    const cli = new SockJSC("http://localhost:" + port +"/xiva");
    cli.onmessage = function (msg) {
        // received some data
        console.info('worker->client', n ,' :: ' , msg.data );
        try {
            this.ondata( JSON.parse(msg.data) );
        } catch (e ){
            console.error('onmessage fail', msg, e);
        }
    };
    cli.ondata = function( data ){
        console.log('sockjs data',data);
    }
    cli.onerror =  function (e) {
        // something went wrong
        //console.log('sockjs error', e);

        console.error('worker error', n ,' :: ' , e );
    };
    cli.senddata = function( data ){
        this.send( JSON.stringify(data ) ) ;
    }
    if( onReady ){
        cli.onopen =  () => {
            // connection is established
                console.log('client', n , 'connected to: ' + port);
                onReady( cli );
        };
    }
    return cli;
}

exports.client = client;


setTimeout( function(){
    console.log('xiva helper Execution time limit 10 sec');
    process.exit( 1 );
}, 10000 );

