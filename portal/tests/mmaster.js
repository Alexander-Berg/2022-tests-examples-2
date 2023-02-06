#!/opt/nodejs/6/bin/node

'use strict';

const config = require('./config.test');
const tools = require('../server/tools');
const cluster = require('cluster');
const assert = require('chai').assert;
const helper = require('./xiva_helper');



const XivaNode = require('../server/XivaNode').XivaNode;
const XivaWSWorker = require('../server/XivaWSWorker').XivaWSWorker;
const net = require('net');

config.masterServers = [
        {host: 'localhost', port: 8011}, //'B'
        {host: 'localhost', port: 8012}, //'C'
];
config.log.write_to_file = false;
config.aggregationTime = 100;
let configB = Object.assign({}, config);
let configC = Object.assign({}, config);

configB.masterServers = [
    {host: 'localhost', port: 8011}, //'B'
];
configC.masterServers = [
    {host: 'localhost', port: 8012}, //'C'
];

let ch = 'stream_A_1';
//masters
let Node2 = new XivaNode( { id: 'B', config: config,  listen: 8011, workerPort: 7010, cluster: 0, workers: 1  });
let Node3 = new XivaNode( { id: 'C', config: config,  listen: 8012, workerPort: 7015, cluster: 0, workers: 1  });
//nodes
let Node1 = new XivaNode( { id: 'A', config: configB, listen: 8010, workerPort: 7000, cluster: 0, workers: 1  });
let Node4 = new XivaNode( { id: 'D', config: configC, listen: 8013, workerPort: 7020, cluster: 0, workers: 1  });

let Nodes = [ Node1, Node2, Node3, Node4 ];
for( let node of Nodes ){
 //   node.connectMasters();
}

setTimeout( ()=> { assert(false, "Exit normally"); process.exit() }, 3000);

let client1 = helper.client(1, 7000, function(){ console.info(' client 1 connected'); client1.senddata( {subscribe: [ch] })} );
let client2 = helper.client(2, 7010, function(){ console.info(' client 2 connected'); client2.senddata( {subscribe: [ch] })} );
let client3 = helper.client(3, 7015, function(){ console.info(' client 3 connected'); client3.senddata( {subscribe: [ch] })} );
let client4 = helper.client(4, 7020, function(){ console.info(' client 4 connected'); client4.senddata( {subscribe: [ch] })} );

let clients = [client1, client2, client3, client4];
let msg = [];

let control = new net.Socket( 'localhost', 8011 );


let controlMsg = [];
let controlSocket = net.createConnection( 8011, 'localhost');
controlSocket.on('data', data => {
    let commands = String(data).split("\n");
    for(let command of commands ){
        if(! command ) continue;
        let d = JSON.parse(command);
        controlMsg.push( d );
    }
});
controlSocket.send = function(data){
    this.write( JSON.stringify( data) );
}



new Promise( ok => {
    setTimeout( ok, 500 )
}).then(ok => {

    let pingAvg = Node2.getPingAvg();
    assert( pingAvg && typeof( pingAvg ) === 'number', 'Pinng AVG');

    Node2.unsubscribeFromSlow();
    Node1.unsubscribeFromSlow();

    assert(Node1.masterSelected , 'Master Selected' );
    assert(Node2.isMaster, "2 Self MAster");
    assert(Node3.isMaster, "3 Self MAster");
    assert(Node4.masterSelected, "MAster selected");

    for(let i =0; i < clients.length; i++){
        msg[i] = {
            messages : [],
            emoji : {},
        }
        clients[i].ondata = function( data ){
            if( data.ok ) return;
            msg[i].messages.push( {
                dt: new Date(),
                data
            } );
            if( data.emoji ){
                for(let ts in data.emoji ){
                    for( let emoji in data.emoji[ts]){
                        msg[i].emoji[emoji] = (msg[i].emoji[emoji] || 0) + 1
                    }
                }
            }
        }
    }


    //for(let i =0; i < 2; i++){
    //    clients[i].senddata({ emoji: 's' + (i), ch});
    //}
    clients[0].senddata({ emoji: 's0', ch});
    controlSocket.send({subscribe_node:1 });


    return new Promise( ok => {
        setTimeout( ok, 500 )
    } );

}).then( result => {
    //console.log(msg);

    assert( !msg[0].emoji['s0'], ' Worker LoopBack');
    assert( msg[1].emoji['s0'], ' Node -> Master -> Worker');
    assert( msg[2].emoji['s0'], ' Node -> Master -> Master');
    assert( msg[3].emoji['s0'], ' Node -> Master -> Master -> Node');


    clients[1].senddata({ emoji: 's1', ch});

    assert( controlMsg[0].node_subscribed, "ControlSocket Subscribed");
    controlMsg.length = 0;
    controlSocket.send({unsubscribe_node:1 });

    return new Promise( ok => {
        setTimeout( ok, 500 )
    } );
}).then( result => {


    assert( controlMsg[0].node_unsubscribed, "ControlSocket UnSubscribed");

    assert( msg[0].emoji['s1'], ' Master -> Node');
    assert( !msg[1].emoji['s1'], 'Master LoopBack');
    assert( msg[2].emoji['s1'], ' Master -> Master ');
    assert( msg[3].emoji['s1'], ' Master -> Master -> Node');

    clients[2].senddata({ emoji: 's2', ch});
    clients[3].senddata({ emoji: 's3', ch});

    return new Promise( ok => {
        setTimeout( ok, 500 )
    } );
}).then( ok => {
    for( let i = 0; i < clients.length; i++){
        console.log( i , '> messages', msg[i].messages );
        console.log( i , '> emoji', msg[i].emoji );
        for( let j = 0; j < clients.length; j++ ){
            if(i === j) continue;
            assert( msg[i].emoji[ 's' + j ] === 1 , ` client ${i} get message from client ${j}` );
        }
    }

    tools.logger.info('controlMsg', controlMsg);
    process.exit();
});





