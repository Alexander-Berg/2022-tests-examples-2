module.exports = function() {
    return req([
        service.q({
            notifications: [
                notification({ id: 'rcnt0', is_read: true, important: true, text: texts.q[0], mtime: dates.recent[4] }),
                notification({ id: 'rcnt1', important: true, text: texts.q[1], mtime: dates.recent[1] }),
                notification({ id: 'rcnt2', important: true, text: texts.q[2], mtime: dates.old[7] }),
                notification({ id: 'rcnt3', important: true, text: texts.q[3], mtime: dates.recent[1] }),
            ],
        }),
        service.market({
            notifications: [
                notification({ id: 'rcnt4', important: true, text: texts.market[4], mtime: dates.recent[2] }),
                notification({ id: 'rcnt5', is_read: true, important: true, text: texts.market[0], mtime: dates.recent[4] }),
                notification({ id: 'rcnt6', important: true, text: texts.market[1], mtime: dates.recent[1] }),
                notification({ id: 'rcnt7', important: true, text: texts.market[2], mtime: dates.old[2] }),
                notification({ id: 'rcnt8', important: true, text: texts.market[3], mtime: dates.recent[6] }),
                notification({ id: 'rcnt9', important: true, text: texts.market[4], mtime: dates.recent[8] }),
            ],
        }),
        service.zen({
            notifications: [
                notification({ id: 'rcnt10', is_read: true, important: true, text: texts.zen[0], mtime: dates.recent[9] }),
            ],
        }),
    ]);
};

// module.exports = function() {
//     return req([
//         service({
//             name: 'Я.Антивирус',
//             id: 'fakeservice0',
//             blocks: [
//                 block({ id: 'rcnt0', text: 'Доступно 123 новых обновления' }),
//                 block({ id: 'rcnt1', text: 'Найдено 123 вируса' }),
//                 block({ id: 'rcnt2', text: 'Можно освободить 123ГБ на жестком диске' }),
//                 block({ id: 'rcnt3', text: 'Производительность компьютера выросла на 20% после Я.Чистки' }),
//             ],
//         }),
//         service({
//             name: 'Я.Чистка',
//             id: 'fakeservice1',
//             blocks: [
//                 block({ id: 'rcnt4', text: 'Экран протетр' }),
//                 block({ id: 'rcnt5', text: 'Кулеры продуты' }),
//                 block({ id: 'rcnt6', text: 'Обои поменяны' }),
//                 block({ id: 'rcnt7', text: 'Биткоин замайнен' }),
//                 block({ id: 'rcnt8', text: '123 пароля было изменено' }),
//                 block({ id: 'rcnt9', text: 'ОШИБКА' }),
//             ],
//         }),
//         service({
//             name: 'Я.Одинок',
//             id: 'fakeservice2',
//             blocks: [
//                 block({ id: 'rcnt10', text: 'Уведомление без друзей :с' }),
//             ],
//         }),
//     ]);
// };
