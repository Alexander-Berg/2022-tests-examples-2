#!/usr/bin/env node
/**
 * Created with PyCharm.
 * User: evbogdanov
 * Date: 17.06.13
 * Time: 18:33
 */

var net = require('net');


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

try{
    channel_key = process.argv[2];
}
catch(err){}

if (typeof(channel_key) === 'undefined'){
    console.log('USAGE: node connections_counter.js <channel>');
    process.exit(1);
}

function send_command(command){
    try{
        var sock = net.Socket();
        sock.setEncoding('utf8');
        sock.connect('/tmp/xivadaemon.sock');

        sock.addListener('data', function(data){
            console.log(data);
            sock.end();
        });
        sock.addListener('error', function(error){
            process.stderr.write(error);
            process.stderr.write('\n');
            process.exit(-1);
            return null;
        });
        sock.write(command);
    }
    catch (err){
        console.log('error while sending command -', err);
        console.log('command is', command);
        return null;
    }
    return true;
}

var command = 'connections ' + channel_key;
send_command(command);
