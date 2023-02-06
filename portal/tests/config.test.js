/*
 Configuration for portal xiva
 */

const config = require('../etc/config');

config.RELEASE = false;
config.DEBUG = !exports.RELEASE;
config.log.write_to_console = true;
config.log.write_to_file = false;
config.log.console_full_colors = true;

config.maxWorkers = 2;

config.selfStatsServer = null;
config.listenSocketPathBase = 7000;
config.selfControlSocket =  '/tmp/test.xivadaemon.sock';
config.controlSocketPathBase= '/tmp/test.xiva_control.{0}.sock';
config.masterServers = [
    { port: 8000, host: 'localhost'},
    { port: 8002, host: 'localhost'},
];


module.exports = config;
