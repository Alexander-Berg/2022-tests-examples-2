// Возвращаю текущий понедельник (getCurrentMonday) и воскресенье (getCurrentSunday) в виде строки в формате DD.MM.YYYY:
// Отталкиваюсь от текущей даты (определяю день недели через getDate() и либо вычитаю дни до понедельника, либо прибавляю
// Через getMonth() возвращаю месяц и прибавляю 1, так как метод возвращает январь = 0
// Через getDate() возвращаю день
// Далее через if привожу к строке вида DD.MM.YYYY, добавляя точки и нули там, где день или месяц однозначное число

const today = new Date();

export function getCurrentMonday() {
    const monday = new Date(today.setDate(today.getDate() - today.getDay() + 1));
    const month = monday.getMonth() + 1;
    const day = monday.getDate();

    if (month < 10 && day < 10) {
        return '0' + day + '.0' + month + '.' + monday.getFullYear();
    } else if (month < 10 && day >= 10) {
        return day + '.0' + month + '.' + monday.getFullYear();
    } else if (month >= 10 && day < 10) {
        return '0' + day + '.' + month + '.' + monday.getFullYear();
    } else {
        return day + '.' + month + '.' + monday.getFullYear();
    }
}

export function getCurrentSunday() {
    const sunday = new Date(today.setDate(today.getDate() + (7 - today.getDay())));
    const month = sunday.getMonth() + 1;
    const day = sunday.getDate();

    if (month < 10 && day < 10) {
        return '0' + day + '.0' + month + '.' + sunday.getFullYear();
    } else if (month < 10 && day >= 10) {
        return day + '.0' + month + '.' + sunday.getFullYear();
    } else if (month >= 10 && day < 10) {
        return '0' + day + '.' + month + '.' + sunday.getFullYear();
    } else {
        return day + '.' + month + '.' + sunday.getFullYear();
    }
}
