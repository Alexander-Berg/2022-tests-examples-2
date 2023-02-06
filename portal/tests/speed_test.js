/**
 * Created with PyCharm.
 * User: evbogdanov
 * Date: 10.07.13
 * Time: 17:54
 */

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


var channels = require('../for_delete/channels');
var connections = require('../for_delete/connections');


var starttime = Date.now();

function next_connection(serial){
    //return format('{0}-{1}-{1}-{1}', serial, Date.now())
    var tmp = Date.now().toString();
    return serial.toString() + '-' + tmp + '-' + tmp + '-' + tmp;
}

channels.add_channel('testchannel');

console.log('started....');
for (var ind = 0; ind < 1000000; ind++){
    var conn_id = next_connection(ind);
    connections.add_connection(conn_id, 'some thing as socket');
    channels.add_channel_client('testchannel', conn_id);
    if (ind % 1000 == 0) process.stdout.write('.');
}
console.log(format('\n\ngenerated {0} connections for time {1}', channels.get_channel_clients('testchannel').length, (Date.now() - starttime)/1000.0));

starttime = Date.now();
var finded = 0;
var clients = channels.get_channel_clients('testchannel');

if (clients == null){
    console.log('testchannel', channels.get_channels());
}
for(var cindex= 0 ; cindex < clients.length; cindex++){
    //var tmp = JSON.stringify({'channelupdate': {channel: 'testchannel', newtimestamp: starttime}});
    finded++;
}

console.log(format('\nfinded: {0}; For the time: {1} sec', finded.toString(), ((Date.now() - starttime)/1000.0).toString()));

console.log('Connection count at start', connections.get_connection_count());
starttime = Date.now();
var deleted = 0;
for(cindex= 0 ; cindex < clients.length; cindex++){
    connections.del_connection(clients[cindex]);
    deleted++;
}

console.log(format('deleted: {0}; For the time: {1} sec', deleted.toString(), ((Date.now() - starttime)/1000.0).toString()));

console.log('Connection count at end', connections.get_connection_count());