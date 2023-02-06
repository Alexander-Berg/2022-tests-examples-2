/**
 * Получаем track_id по выполнению команды Passport.debug.getTrackID()
 */
module.exports.yaGetTrackId = async function() {
    await this.waitUntil(() => this.execute(() => typeof Passport !== undefined));

    /* global Passport */
    return await this.execute(() => Passport.debug.getTrackID());
};
