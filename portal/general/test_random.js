"use strict";
const config = require('../etc/config.json');
const db = require('../server/libs/db');
const achievements = require('../server/api/v1/achievements');
const tools = require('../server/tools');


db.connect()
    .then(() => {
        db.get_random()
            .then(data => {
                data.forEach(a => {
                    const d = achievements.format_achievement(a);
                    let text = '';
                    if (d.requests) {
                        text += `${d.raw.requests}\t${d.raw.mobile_requests}\t${d.stat_weeks}\t`;
                        text += `${d.requests} ${d.texts && d.texts.requests} (больше чем у ${d.requests_percentile}%)\t`;
                        text += `${d.mobile_requests} ${d.texts && d.texts.mobile} (больше чем у ${d.mobile_requests_percentile}%)\t`;
                        text += `${d.texts && d.texts.requests_from.replace('%s', d.city_from)}\t`;
                        text += `${d.misspells} ${d.texts && d.texts.misspells} (больше чем у ${d.misspells_percentile}%)\t`;
                        text += `${d.suggests} ${d.texts && d.texts.suggests} (больше чем у ${d.suggests_percentile}%)\t`;
//                    text += `${d.visits_portal} ${d.texts && d.texts.requests} на морду\nбольше чем у ${d.visits_portal_percentile}%`;
//                    text += `${d.dates_in_portal} проведено на портале\n${1}`;
                        text += `${d.texts && d.texts.categories}: "${d.categories.join('/')}"\t`;
                        if (d.cookie_days) {
                            text += `Куке ${d.cookie_days} дней`;
                        }
                        // console.log(text);
                    }
                });
                db.disconnect();
            });
    });