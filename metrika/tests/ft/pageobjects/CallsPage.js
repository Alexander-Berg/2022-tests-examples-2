const Page = require('./Page.js');

const addFirstTrackBtn = '.calls__center .button_size_l.button_theme_action';
const addTrackBtn = '.calls__center .calls__add-number';
const editTrackBtn = '.track:first-child button.track__edit-button';
const trackPopup = '.popup .track-edit';
const trackField = '.track-edit__dn-col input';
const saveTrackBtn = '.track-edit__footer .track-edit__save';
const deactivateTrackBtn = '.track-edit__footer .track-edit__deactivate';
const trackList = '.track-list__list';
const trackInList = '.track-list__list .track__info-panel-wrap';
const confirmPopup = '.popup__content .i-confirm-popup__popup-content';
const confirmPopupBtn = '.popup__content .i-confirm-popup__popup-content .button_action_confirm';

const NUMBER_LENGTH = 7;

class CallsPage extends Page {
    async open() {
        await this.browser.url('/calls');
    }

    async createTrack() {
        if (await this.browser.$(addTrackBtn)) {
            await this.browser
                .click(addTrackBtn)
                .waitForVisible(trackPopup);
        } else {
            await this.browser
                .waitForVisible(addFirstTrackBtn)
                .click(addFirstTrackBtn)
                .waitForVisible(trackPopup);
        }
        await this.fillNumber();
        await this.browser
            .click(saveTrackBtn)
            .pause(2000)
            .click('.track-edit__info-popup .button_pseudo_yes.track-edit__popup-close');

    }

    async fillNumber() {
        await this.browser
            .element(trackField)
            .setValue(this.getRandomNumber(NUMBER_LENGTH));
    }

    async countTracks() {
        const tracks = await this.browser.waitForExist(trackList).elements(trackInList);
        return tracks.value.length;
    }

    async removeAllTracks() {
        const tracks = await this.countTracks();
        for(let i = 0; i < tracks; i++) {
            await this.browser
                .refresh()
                .pause(2000)
                .waitForVisible(editTrackBtn)
                .click(editTrackBtn)
                .waitForVisible(trackPopup)
                .click(deactivateTrackBtn)
                .waitForVisible(confirmPopup)
                .click(confirmPopupBtn);
        }
    }
}

module.exports = {
    CallsPage,
};
