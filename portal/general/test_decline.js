const tools = require('../server/tools');
const l10n = require('../server/libs/l10n');


console.log(tools.decline(1.5, ['месяц', 'месяца', 'месяцев']));
console.log(l10n.decline_l10n(0, 'thanks_main.suggests', 'ru'))
