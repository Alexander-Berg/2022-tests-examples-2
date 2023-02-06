const tools = require('../tools');


var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

function get_hours(hours, lang) {
    if (!hours) {
        return '';
    }
    // Благодаря геопоиску мы имеем данные по часовому поясу - hours.tzOffset
    var nowtime = new Date(new Date().getTime() + (hours.tzOffset / 60 + new Date().getTimezoneOffset()) * 60000);
    var intervals = false;
    var day = days[nowtime.getDay() - 1];
    for (var i = 0; i < hours.Availabilities.length; i++) {
        if (hours.Availabilities[i].Everyday) {
            if (hours.Availabilities[i].TwentyFourHours) {
                return i18n.get('time.24hours', lang);
            }
            else {
                intervals = hours.Availabilities[i].Intervals;
                break;
            }
        }
        if (hours.Availabilities[i][day]) {
            if (hours.Availabilities[i].TwentyFourHours) {
                return i18n.get('time.24hours', lang);
            }
            else {
                intervals = hours.Availabilities[i].Intervals;
                break;
            }
        }
    }
    var text = '', int, from, to, int_i;
    if (intervals) {
        if (intervals.length == 1) {
            int = intervals[0];
            from = new Date();
            to = new Date();
            from.setHours(parseInt(int.from.split(':')[0]));
            from.setMinutes(parseInt(int.from.split(':')[1]));
            from.setSeconds(0);
            to.setHours(parseInt(int.to.split(':')[0]));
            to.setMinutes(parseInt(int.to.split(':')[1]));
            to.setSeconds(0);
            //from = Date.parse(int.from);
            //to = Date.parse(int.to);
            if (to < from) {    // Добавляем сутки к "концу" интервала, если он в следующих сутках
                if (nowtime < to) { // Скорее всего на часах - после полуночи
                    nowtime.add(1).days();  // грязный хак
                }
                to.add(1).days();
            }
            if (to > nowtime) { // Вообще делаем действия только если интервал не кончился
                var tmp = new Date();
                tmp.setHours(parseInt(int.from.split(':')[0]));
                tmp.setMinutes(parseInt(int.from.split(':')[1]));
                tmp.setSeconds(0);
                if (tmp.add(3).hours() > nowtime) {
                    text += from.toString("HH:mm") + '–' + to.toString("HH:mm");
                }
                else {
                    text += tools.format(i18n.get('time.untill', lang), to.toString("HH:mm"));
                }
            }

        }
        else {
            for (int_i = 0; int_i < intervals.length; int_i++) {
                int = intervals[int_i];
                from = new Date();
                to = new Date();
                from.setHours(parseInt(int.from.split(':')[0]));
                from.setMinutes(parseInt(int.from.split(':')[1]));
                from.setSeconds(0);
                to.setHours(parseInt(int.to.split(':')[0]));
                to.setMinutes(parseInt(int.to.split(':')[1]));
                to.setSeconds(0);
                if (to < from) {    // Добавляем сутки к "концу" интервала, если он в следующих сутках
                    if (nowtime < to) { // Скорее всего на часах - после полуночи
                        nowtime.add(1).days();  // грязный хак
                    }
                    to.add(1).days();
                }
                if (to > nowtime) { // Вообще делаем действия только если интервал не кончился
                    if (text || int_i < intervals.length - 1) { // Индикатор, что это не последний интервал
                        if (text) {
                            text += ', ';
                        }
                        text += from.toString("HH:mm") + '–' + to.toString("HH:mm");
                    }
                    else {
                        text = tools.format(i18n.get('time.untill', lang), to.toString("HH:mm"));
                    }
                }
            }
        }
        return tools.capitalize(text);
    }
    else {
        tools.logger.error(JSON.stringify(hours.Availabilities), hours.text);
    }
}

let cases = [
    {
        datetime: '2016-11-14 19:19:06.639',
        Availabilities: [{
            "Tuesday": true,
            "Wednesday": true,
            "Thursday": true,
            "Friday": true,
            "Saturday": true,
            "Intervals": [{"from": "09:00,:'00", "to": "18:00:00"}]
        }],
        text: 'вт-сб 9:00–18:00'
    },
    {
        datetime: '2016-11-14 20:26:59.093',
        Availabilities: [{
            "Tuesday": true,
            "Wednesday": true,
            "Thursday": true,
            "Friday": true,
            "Intervals": [{"from": "00:00:00", "to": "08:00:00"}]
        }, {"Saturday": true, "Intervals": [{"from": "08:10:00", "to": "00:00:00"}]}, {
            "Sunday": true,
            "Intervals": [{"from": "08:10:00", "to": "08:00:00"}]
        }],
        text: 'вт-пт 0:00–8:00; сб 8:10–0:00; вс 8:10–8:00'
    },
    {
        datetime: '2016-11-14 20:20:15.763',
        Availabilities: [{
            "Tuesday": true,
            "Wednesday": true,
            "Thursday": true,
            "Friday": true,
            "Intervals": [{"from": "07:00:00", "to": "22:00:00"}]
        }, {"Saturday": true, "Intervals": [{"from": "22:00:00", "to": "07:00:00"}]}, {
            "Sunday": true,
            "Intervals": [{"from": "22:00:00", "to": "22:00:00"}]
        }],
        text: 'вт-пт 7:00–22:00; сб 22:00–7:00; вс 22:00–22:00'
    },
    {
        datetime: '2016-11-14 20:24:33.853',
        Availabilities: [{"Monday": true, "Saturday": true, "Intervals": [{"from": "09:00,:'00", "to": "04:00:00"}]}],
        text: 'пн,сб 9:00–4:00'
    },
];

for (let i in cases) {
    console.log(cases[i]);
    console.log(get_hours(cases[i], 'ru'));
}