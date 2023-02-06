#!/opt/nodejs/6/bin/node
/**
 * Created with PyCharm.
 * User: evbogdanov
 * Date: 06.08.13
 * Time: 16:37
 */

const format = require("../server/tools.js").format;

const connection_url = 'http://localhost/xiva/333/3333333/websocket';
const statuses = {
    cs: {exit_code: 0, message: null},
    ss: {exit_code: 0, message: null}
};


function test_client_side() {
    const WebSocketClient = require('websocket').client;

    const client = new WebSocketClient();
    client.on('connectFailed', error => {
        statuses.cs.message = `connection failed: ${error && error.split('\n')[0]}`;
        statuses.cs.exit_code = 2;
    });

    client.on('connect', connection => {
        connection.on('error', error => {
            try {
                statuses.cs.message = `Connection Error: ${error && error.toString()}`;
                statuses.cs.exit_code = 2;
            }
            catch (error) {
                statuses.cs.message = `error while logging errors - ${error && error.toString()}`;
                statuses.cs.exit_code = 2;
            }
        });
        connection.on('close', () => {
            statuses.cs.message = 'connection closed';
            statuses.cs.exit_code = 2;
        });
        connection.on('message', message => {
        });
        if (connection.connected) {
            const channel_list = {subscribe: {'testchannel_1': parseInt(Date.now())}};
            connection.sendUTF(JSON.stringify(channel_list));
            setTimeout(() => {
                statuses.cs.message = 'connection established';
                statuses.cs.exit_code = 0;
            }, 500);
        }
    });
    client.connect(connection_url);
}

function test_server_side() {
    const net = require('net');

    try {
        const sock = net.Socket();
        sock.setEncoding('utf8');
        sock.connect('/tmp/xivadaemon.sock');

        sock.addListener('data', data => {
            const died = parseInt(data[0]);
            if (died == 0) {
                statuses.ss.message = 'answer recieved';
                statuses.ss.exit_code = 0;
            }
            else {
                statuses.ss.message = `answer recieved, but workers died: ${died.toString()}`;
                if (died > 3) statuses.ss.exit_code = 2;
                else statuses.ss.exit_code = 1;
            }
            sock.end();
        });
        sock.addListener('error', error => {
            statuses.ss.message = `Socket error: ${error && error}`;
            statuses.ss.exit_code = 2;
            return null;
        });
        sock.write('stats');
    }
    catch (error) {
        statuses.ss.message = `can't connect to server - ${error && error.toString()}`;
        statuses.ss.exit_code = 2;
        return null;
    }
    return true;
}

test_client_side();
test_server_side();

function check_statuses() {
    if (statuses.cs.exit_code == null || statuses.ss.exit_code == null) {
        setTimeout(check_statuses, 200);
        return;
    }
    console.log(format('PASSIVE-CHECK:{0};{1};CS:{2}; SS:{3}',
        'portal_xiva',
        Math.max(statuses.cs.exit_code, statuses.ss.exit_code),
        statuses.cs.message,
        statuses.ss.message));
    process.exit(Math.max(statuses.cs.exit_code, statuses.ss.exit_code));
}

check_statuses();

function final_timeout() {
    if (statuses.cs.exit_code == null) {
        statuses.cs.exit_code = 2;
        statuses.cs.message = 'Timeout';
    }
}

setTimeout(final_timeout, 5000);
