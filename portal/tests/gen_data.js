'use strict';
const _ = require('lodash');
const Promise = require('bluebird');


const achievements_list = _.range(50).map(r => `ach${r}`);

const yandexuids = new Set();

const gen_yandexuid = () => {
    const yuid = `${parseInt(Math.random() * 999000000 + 1000000)}${parseInt(Date.now() / 1000)}`;
    return !yandexuids.has(yuid) ? yandexuids.add(yuid) && yuid : gen_yandexuid();
};
const gen_achievements = () => achievements_list.filter(() => Math.random() < 0.05);
const gen_user_data = () => {
    return {
        yandexuid: gen_yandexuid(),
        data: JSON.stringify(gen_achievements())
    }
};

process.stdout.write('INSERT INTO achievements VALUES ');
_.range(250000).map(() => {
    const data = gen_user_data();
    process.stdout.write(`(${data.yandexuid}, ${JSON.stringify(data.data)}),`);
});

const data = gen_user_data();

process.stderr.write(yandexuids.size + '\n\n');
process.stdout.write(`(${data.yandexuid}, ${JSON.stringify(data.data)})`);
process.stdout.write(';');

// db.connect()
//     .then(() => {
//             // _.range(1000).map(() => db.insert(gen_user_data())))
//         db.insert_bulk(_.range(1000).map(() => gen_user_data()))
//             .then(() => tools.logger.info('ok!'))
//             .catch(error => tools.logger.error('error:', error))
//             .then(() => process.exit(0));
//     });
//
