/*
* 1) указание интерфейса
* 2) меньше информации в консоль
* 3) учет лага на основе пришедших данных
*
*
* */


//first, checks if it isn't implemented yet
function format(format_string) {
    var args = arguments;
    return format_string.replace(/{(\d+)}/g, function(match, number) {
        number = (parseInt(number) + 1).toString();
        return typeof args[number] != 'undefined'
            ? args[number]
            : match
            ;
    });
}


var connection_url = null;

try{
    connection_url = process.argv[2];
}
catch(error){
}

if (typeof(connection_url) == 'undefined'){
    console.log('USAGE: node script.js <Connection URL>');
    process.exit(1);
}

var clients = [];
var connectionFailed = 0;
var closedNormally = 0;
var connectionFailedMessages = [];

function create_client_2(){
    var WebSocketClient = require('websocket').client;

    var client = new WebSocketClient();
    client.on('connectFailed', function(error) {
        if (connectionFailedMessages.indexOf('Connect Error: ' + error.toString()) < 0){
            connectionFailedMessages.push('Connect Error: ' + error.toString());
        }
        connectionFailed++;
    });

    client.on('connect', function(connection) {
        clients[connection.socket._httpMessage._headers['sec-websocket-key']] = {};
        connection.on('error', function(error) {
            try{
                delete clients[connection.socket._httpMessage._headers['sec-websocket-key']];
            }
            catch(err){
                console.log('error while handle errors - ', err.toString());
            }
        });
        connection.on('close', function() {
            delete clients[connection.socket._httpMessage._headers['sec-websocket-key']];
            closedNormally++;
        });
        connection.on('message', function(message) {
        });
        if (connection.connected) {
            var channel_list = {subscribe: {'testchannel_1': parseInt(Date.now())}};
            for(var ind = 0; ind < 5; ind++)
            {
                var channel = '';
                do {
                    channel = Math.round(Math.random()*300000).toString()
                } while (channel_list.subscribe.hasOwnProperty(channel));
                channel_list.subscribe[channel] = parseInt(Date.now());
            }
            connection.sendUTF(JSON.stringify(channel_list))
        }
        setTimeout(function(){
            connection.close();
        }, 15000)
    });
    client.connect(connection_url);
}

var i = 0;
function newclient(){
    if (i < 100000000){
        i++;
        create_client_2();
        setTimeout(newclient, 5);
    }
}
newclient();

function watcher(){
    console.log(format('connects: {0}, Failed: {1}, Closed normally: {2}', Object.keys(clients).length, connectionFailed, closedNormally));
    setTimeout(watcher, 2000);
}
watcher();
