/*
* 1) указание интерфейса
* 2) меньше информации в консоль
* 3) учет лага на основе пришедших данных
*
*
* */


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

var connections_count = 2500;
var outInterface = null;
var connection_url = null;

try{
    outInterface = process.argv[2];
    connections_count = parseInt(process.argv[3]);
    connection_url = process.argv[4];
}
catch(error){
}

if (typeof(outInterface) == 'undefined' || typeof(connection_url) == 'undefined' || isNaN(connections_count)){
    console.log('USAGE: node script.js <OutInterface> <ConnectionCount> <Connection URL>');
    process.exit(1);
}

var clients = [];
var connectionFailed = 0;
var connectionClosed = 0;
var connectionFailedMessages = [];
var clients_info = {};

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
        clients.push(connection);
        clients_info[clients.indexOf(connection)] = {};
        connection.on('error', function(error) {
            try{
                clients_info[clients.indexOf(connection)].error = "Connection Error: " + error.toString();
                console.log("Connection Error: " + error.toString());
            }
            catch(err){
                console.log('error while logging errors - ', err.toString());
            }
        });
        connection.on('close', function() {
            connectionClosed++;
            delete clients_info[clients.indexOf(connection)];
        });
        connection.on('message', function(message) {
            if (message.type === 'utf8') {
                if (message.utf8Data == 'o'){
                }
                else if (message.utf8Data == 'h'){
                    connection.send('');
                }
                else{
                    var new_message = '';
                    if (message.utf8Data[0] == 'a') {
                        new_message = JSON.parse(message.utf8Data.substring(1))[0];
                    }
                    else {
                        new_message = message.utf8Data;
                    }
                    do_control(connection, new_message);
                }
            }
        });
        if (connection.connected) {
            var channel_list = {subscribe: {'testchannel_1': parseInt(Date.now())}};
            for(var ind = 0; ind < 2; ind++)
            {
                var channel = '';
                do {
                    channel = Math.round(Math.random()*3000).toString()
                } while (channel_list.subscribe.hasOwnProperty(channel));
                channel_list.subscribe[channel] = 0;
            }
            connection.sendUTF(JSON.stringify(channel_list))
        }
    });
    client.connect(connection_url, null, null, null, outInterface);
}

var i = 0;
function newclient(){
    if (i < connections_count){
        i++;
        create_client_2();
        setTimeout(newclient, 2);
    }
}
newclient();

function watcher(){
    var errors = 0;
    var error_texts = [];
    for (var client in clients_info){
        if (!clients_info.hasOwnProperty(client)) continue;
        if (!clients_info[client].hasOwnProperty('timedelta')) continue;
        if (clients_info[client].hasOwnProperty('error')){
            errors++;
            if (error_texts.indexOf(clients_info[client].error) < 0){
                error_texts.push(clients_info[client].error);
            }
        }
    }
    console.log(format('connects: {1}, closed: {3}, with error: {0}, failed: {2}',
                    errors,
                    Object.keys(clients_info).length,
                    connectionFailed,
                    connectionClosed
                    )
                );
    if (error_texts.length > 0) console.log(error_texts);
    if (connectionFailedMessages.length > 0) console.log(connectionFailedMessages);
    setTimeout(watcher, 2000);
}
watcher();


function do_control(connection, control_messages){
    var command_regexp = /^XivaUpdate\({\'ch\' : \'(.*?)\', \'key\' : \'(.*?)\', \'ts\' : '(\d*?)'}\);$/;
    var res = control_messages.match(command_regexp);
    if (res == null){
        return false;
    }
    var channel_id = res[1] + '_' + res[2];
    var channel_timestamp = res[3];
    update_channel(connection, channel_id, channel_timestamp); //, message);
    return null;
}
function update_channel(connection, channel_id, channel_timestamp, message){
    if (channel_id == 'testchannel_1'){
        clients_info[clients.indexOf(connection)].timedelta = Date.now() - parseInt(channel_timestamp);
    }
}
