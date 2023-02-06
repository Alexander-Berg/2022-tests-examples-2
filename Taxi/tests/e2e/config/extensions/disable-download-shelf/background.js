/* eslint-disable no-undef */
chrome.runtime.onInstalled.addListener(() => {
    chrome.downloads.setShelfEnabled(false);
});
