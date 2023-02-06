#!/opt/nodejs/6/bin/node

'use strict';

const config = require('./config.test');
const tools = require('../server/tools');
const cluster = require('cluster');
const assert = require('chai').assert;
const helper = require('./xiva_helper');



const XivaNode = require('../server/XivaNode').XivaNode;
const XivaWSWorker = require('../server/XivaWSWorker').XivaWSWorker;

config.masterServers = [
        {host: 'localhost', port: 8011}, //'B'
        {host: 'localhost', port: 8011}, //'C'
];
config.log.write_to_file = false;

let Node  = new XivaNode( { id: 'A', config: config, listen: 8010, workerPort: 7000, cluster: 0, workers: 3  });
let Node1 = new XivaNode( { id: 'B', config: config, listen: 8011, workerPort: 7010, cluster: 0, workers: 1  });
let Node2 = new XivaNode( { id: 'C', config: config, listen: 8012, workerPort: 7015, cluster: 0, workers: 1  });

let Nodes = [ Node, Node1, Node2 ];

assert( XivaNode.shortHostName( 'xiva-rc.yandex.net') === 'xiva-rc', 'xivarc short hostname');
assert( XivaNode.shortHostName( 's1.pxiva.yandex.net') === 's1', 's1 short hostname');
assert( XivaNode.shortHostName( 's1') === 's1', 's1 short hostname');

if(cluster.isMaster) {
    tools.logger.info('----------- START TESTING --- ');
    assert.equal(  Object.keys(Node.workers).length, 3 , "3 workers spawned");
    for( let node of Nodes ){
        node.connectMasters();
    }



    let client1;
    let client2;
    //B client
    let client3 = helper.client(3, 7010, function(){ console.info(' client 3 connected'); client3.senddata( {subscribe: ['stream_emoji_1'] })} );
    //C client
    let client4 = helper.client(4, 7015, function(){ console.info(' client 4 connected'); client4.senddata( {subscribe: ['stream_emoji_1'] })} );
    new Promise( ( ok , fail ) => {
        client1 = helper.client( 1,  7000 , ok );
    }).then( result => {
        console.info('client 1 connected');
        //Connected
        tools.logger.info('----------- START client 2  --- ');
        return new Promise( ( ok, fail ) =>{
            client2 = helper.client( 2, 7001, ok );
        });
    }).then( result => {
        console.info('client 2 connected');
        client1.senddata( { subscribe: [ 'stream_emoji_1' ] });

        tools.logger.info('----------- subscrutbe cleint 1  --- ');
        return new Promise( (ok_sub) => {
            client1.ondata = function(data){ console.log('client 1 data:', data );ok_sub( data ); };
        } );
    }).then(
        function(result){
            console.log('client 1 subscribed:', result );
            console.log(client1.channels);
            client2.messages =  [];
            client2.ondata = function (data){
                client2.messages.push(data);
            }
            client2.senddata( { subscribe: [ 'stream_emoji_1' ] });
            client2.senddata( { ch: 'stream_emoji_1', ms: new Date().getTime(), emoji: 'smile'} )

            tools.logger.info('----------- client 2 send message  --- ');
            return new Promise( ok => {
                client1.ondata = function(data){ ok( data ); };
            });
        },
        function(fail){
            throw Error(fail);
    }).then( result => {

        tools.logger.info('----------- client 1 recive message  --- ');
        //console.log('Client 1 answer', result );
        assert( result.emoji, "Emoji broadcasted to local worker" );
        for( let ts in  result.emoji ){
            assert( String(ts).match(/^\d+(.\d)?$/) , "ts is int(with on decimal)");
        }
        //setInterval( () => { process.exit(); }, 2000 );


        for( let node of Nodes ){
            node.clearAggregation();
        }
        client2.senddata( { ch: 'stream_emoji_1', ts: (new Date().getTime())/1000, emoji: 'hope'} )
        client1.close();
        return new Promise( ok => {
            client4.ondata = function( data){ ok(data) }
        });
    }).then( result => {
        console.log('Client4 message: ', result);
        assert( result.emoji, "Emoji broadcasted to remote worker" );



        console.log('CLIENT2 MESSAGES:',client2.messages);
        assert( client2.messages.length >= 3 , 'C2:  more 3 messages');
        let onsub  = client2.messages.shift();
            assert( onsub.id == 'subscribe' , " C2-0 Subscribe message");
            assert( onsub.ok , " Subscribed ok")
            assert( onsub.mts , " Server gives us time");
            assert( onsub.subscribed, "Subscribed list");
        let onemo  = client2.messages.shift();
            assert( onemo.id == 'emoji' , "C2-1 emoji-ok message");
            assert( onemo.ok , "ok")
        onemo  = client2.messages.shift();
            assert( onemo.id == 'emoji' , "C2-1 emoji-ok message");
            assert( onemo.ok , "ok")

        process.exit();
    });
    //Node.sendWorkerMessage( 2, { 'command': 'exit' })

}
//Node.spawn({});

