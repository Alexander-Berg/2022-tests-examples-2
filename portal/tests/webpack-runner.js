const path = require('path');
const webpack = require('webpack');

module.exports = function (config) {
    return new Promise((resolve, reject) => {
        webpack(config, (error, stats) => {
            if (error) {
                reject(error);
            }
            const json = stats.toJson();

            if (stats.hasErrors()) {
                console.error(json.errors);
                reject(json.errors[0]);
            }

            let assets = {};
            if (json.assets) {
                for (const key in json.assets) {
                    const asset = json.assets[key];
                    const origName = asset.info.sourceFilename;
                    const name = origName || asset.name;
                    assets[name] = path.resolve(json.outputPath, asset.name);
                }
            } else {
                for (const child of json.children) {
                    for (const key in child.assets) {
                        const asset = child.assets[key];
                        const origName = asset.info.sourceFilename;
                        const name = origName || asset.name;
                        assets[name] = path.resolve(child.outputPath, asset.name);
                    }
                }
            }

            resolve({
                warnings: json.warnings,
                assets,
                json
            });
        });
    });
};
