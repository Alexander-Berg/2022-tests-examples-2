const casper = require('casper').create({
    logLevel: "debug",
    // pageSettings: { javascriptEnabled:  true },
});

const errors = []

casper.on("page.error", function(msg, trace) {
  this.echo("Error:    " + msg, "ERROR");
  this.echo("file:     " + trace[0].file, "WARNING");
  this.echo("line:     " + trace[0].line, "WARNING");
  this.echo("function: " + trace[0]["function"], "WARNING");
  this.echo("trace:\n" + trace.map(function(msg){
    return msg.file + ":" + msg.line + (msg['function'] ? ", in " + msg['function'] : '')
  }).join("\n"), "WARNING");
  errors.push(msg);
});

casper.on("remote.message", function(message) {
  this.echo(message);
});

// Opens casperjs homepage
casper.start('https://webvisor.local/page/test', function() {
  this.evaluate(function sendLog(log) {
    // you can access the log from page DOM
    if(Object.prototype.toString.call(log) !== '[object Array]'){
      console.log(log);
    }
  }, this.result.log);
});

casper.run(function(){
  if (errors.length > 0) {
    this.echo(errors.length + ' Javascript errors found', "WARNING");
  } else {
    this.echo(errors.length + ' Javascript errors found', "INFO");
  }
  casper.exit();
})
