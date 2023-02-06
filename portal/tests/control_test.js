#!/opt/nodejs/6/bin/node
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


var close_connection = true;
try{
    message_type = process.argv[2];
    channel_key = process.argv[3];
}
catch(err){}

if (typeof(message_type) == 'undefined'){
    console.log('USAGE: node control_test.js <Message type: stats, debug_on, debug_off, msg <channel_key>, connections, list or list <channel>>');
    process.exit(1);
}

function send_command(command){
    try{
        var sock = net.Socket();
        sock.setEncoding('utf8');
        sock.connect('/tmp/xivadaemon.sock');

        sock.addListener('data', function(data){
            console.log('Answer from xiva:\n' + data);
            sock.end();
        });
        sock.addListener('error', function(error){
            console.log('Some error in socket -', error);
            return null;
        });
        sock.write(command);
        if (close_connection) sock.end();
    }
    catch (err){
        console.log('error while sending command -', err);
        console.log('command is', command);
        return null;
    }
    return true;
}

timestamp = Date.now();

switch (message_type){
    case 'msg':
        command = format("msg www/{0}:{1} XivaUpdate({'ch' : '{2}', 'key' : '{3}', 'ts' : '{1}'});", channel_key, timestamp, channel_key.split('_')[0], channel_key.split('_')[1]);
        close_connection = true;
        break;
    case 'list':
        if (typeof(channel_key) == 'undefined'){
            command = 'list';
        }
        else command = 'list' + ' ' + channel_key;
        close_connection = false;
        break;
    case 'stats':
        command = 'stats';
        close_connection = false;
        break;
    case 'connections':
        if (typeof(channel_key) == 'undefined'){
            console.log('Please, enter some channel');
            process.exit();
        }
        command = 'connections ' + channel_key;
        close_connection = false;
        break;
    case 'debug_on':
        command = 'debug 1';
        close_connection = true;
        break;
    case 'debug_off':
        command = 'debug 0';
        close_connection = true;
        break;
    case 'ping':
        command = 'ping';
        close_connection = false;
        break;
    case 'mobro1':
        command = 'msg www/news_1:0 {"widget_id": "news", "content": "some new content for widget #1"}';
        close_connection = false;
        break;
    case 'mobro2':
        command = 'msg www/wether_1:0 {"widget_id": "wether", "content": "some new content for widget #2"}';
        close_connection = false;
        break;
    case 'mobro3':
        command = 'msg www/auto_1:0 {"widget_id": "auto", "content": "some new content for widget #3"}';
        close_connection = false;
        break;
    case 'mobro4':
        command = 'msg www/holodilnik_1:0 {"widget_id": "holodilnik", "content": "some new content for widget #4"}';
        close_connection = false;
        break;
    default:
        console.log('Unknown command!');
        process.exit();
}
console.log('Command for server: ', command);
send_command(command);
