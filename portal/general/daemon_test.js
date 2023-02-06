#!/usr/bin/env node
/**
 Сервис пробки на маршруте
 Jams on my way
 ***/

var tools = require('./tools');
var config = require('./config.js');

tools.log('"Jams on my way" daemon started. Starting debug server. PID:', process.pid);

try{
    process.env.num = 0;
    require("./daemon.js").start();
}
catch(e){
    tools.log('Debug worker. Exception -', e.toString());
}
