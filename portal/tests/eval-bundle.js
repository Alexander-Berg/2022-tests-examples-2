const vm = require('vm'),
    util = require('util'),
    fs = require('fs');

module.exports = function evalBundle(name, file) {
    return util.promisify(fs.readFile)(file)
        .then(src => {
            const logged = [],
                erred = [],
                log = (...args) => {
                    console.log(...args);
                    logged.push(args.join(','));
                },
                err = (...args) => {
                    console.error(...args);
                    erred.push(args.join(','));
                };
            console.log(`~~~~ Eval bundle ${name} ~~~~`);
            const res = vm.runInNewContext(src, {
                console: {
                    log: log,
                    trace: log,
                    error: err,
                    warn: err
                }
            }, {
                filename: file
            });
            console.log(res);
            console.log(`~~ End eval bundle ${name} ~~`);
            return {
                res,
                logged: logged,
                erred: erred
            };
        });
};
