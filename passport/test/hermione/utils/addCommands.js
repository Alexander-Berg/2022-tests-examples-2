const fs = require('fs');
const path = require('path');

/**
 * Добавляет команды Hermione из указанной папки в браузер
 * @param {Browser} browser
 * @param {String} dir
 */
module.exports = function addCommands(browser, dir) {
    const commandsDir = path.resolve(__dirname, dir);

    fs.readdirSync(commandsDir)
        .filter(function(name) {
            return path.extname(name) === '.js' && fs.statSync(path.resolve(commandsDir, name)).isFile();
        })
        .forEach(function(filename) {
            const commandsFile = require(path.resolve(commandsDir, filename));

            Object.keys(commandsFile).forEach((commandName) => {
                browser.addCommand(commandName, commandsFile[commandName]);
            });
        });
};
