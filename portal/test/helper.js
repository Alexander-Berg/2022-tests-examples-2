const fs = require('fs');
const write = fs.writeFileSync;

function updateMock(mock, name) {
    write(`./test/mocks/results/${name}.json`, JSON.stringify(mock));
}

module.exports = {
    updateMock
}