const testrunner = require("qunit"),
    fs = require('fs'),
    path = require('path');

function getFilesAndTestsForDir(dir){
    const codeDir = path.resolve(dir),
        testsDir = path.resolve(path.join('tests', dir)),
        files = fs.readdirSync(codeDir);

    return files.map(function(file){
        return {
            code: {path: path.join(dir, file), namespace: 'code'},
            tests: path.join(testsDir, file)
        };
    });
}
const testsPack = [].concat(getFilesAndTestsForDir('lib'), getFilesAndTestsForDir('methods'));
console.log(testsPack);
testrunner.run(testsPack, function(result){
    console.log(result);
});
