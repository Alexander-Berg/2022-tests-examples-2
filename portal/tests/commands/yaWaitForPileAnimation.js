const waitForDisapear = async function(selector, errorMsg) {
    if (errorMsg && !this.$(selector).isExisting()) {
        throw new Error(errorMsg);
    }
    await this.$(selector).waitForExist({ reverse: true });
};

module.exports = async function yaWaitForPileAnimation(type) {
    let sel;
    let msg;
    switch (type) {
        case 'expand': [msg, sel] = ['NotificationPile_animation_expand', 'Нет анимации раскрытия']; break;
        case 'collapse': [msg, sel] = ['NotificationPile_animation_collapse', 'Нет анимации закрытия']; break;
        case 'delete': [msg, sel] = ['NotificationPile_animation_delete', 'Нет анимации удаления']; break;
        default: throw new Error('Неизвестный тип анимации');
    }
    await waitForDisapear.call(this, sel, msg);
};
