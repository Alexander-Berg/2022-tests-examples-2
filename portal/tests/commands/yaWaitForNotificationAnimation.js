const waitForDisapear = async function(selector, errorMsg) {
    if (errorMsg && !this.$(selector).isExisting()) {
        throw new Error(errorMsg);
    }
    await this.$(selector).waitForExist({ reverse: true });
};

module.exports = async function yaWaitForNotificationAnimation(type, pile) {
    let sel;
    let msg;
    switch (type) {
        case 'delete': [msg, sel] = ['Notification_animation_delete', 'Нет анимации удаления']; break;
        default: throw new Error('Неизвестный тип анимации');
    }
    let counterEl = await this.$(pile.HeaderCounter());
    let counterBefore;
    if (counterEl) {
        counterBefore = Number(await counterEl.getText());
    }
    await waitForDisapear.call(this, sel, msg);
    if (counterBefore > 2) {
        await this.waitUntil(async() => {
            const counterAfter = Number(await counterEl.getText());
            return counterAfter === counterBefore - 1;
        });
    }
};
