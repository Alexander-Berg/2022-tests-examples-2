/* globals replacedVal $ response */

function stopScroll(actions) {
    actions.executeJS(function () {
        document.body.style.overflow = 'hidden';
    });
}

function enableScroll(actions) {
    actions.executeJS(function () {
        document.body.style.overflow = 'hidden';
    });
}

function setTvBackgroundColor(actions) {
    actions.executeJS(function () {
        document.querySelector('.rows__row_main').style.backgroundColor = '#4eb0da';
        document.querySelector('.rows__row_foot').style.backgroundColor = '#4eb0da';
    });
}

function clearSuggestMiniInput(actions) {
    actions.executeJS(function () {
        document.querySelector('.mini-suggest__input').value = '';
    });
}

function scrollToArrow(actions) {
    actions.executeJS(function () {
        window.scrollTo('5', document.querySelector('.edadeal').offsetTop.toString());
    });
}

function setHeigthInput(actions) {
    actions.executeJS(function () {
        document.querySelector('.mini-suggest').style.height = '900px';
    });
}

function showSkinGreetingPopup(actions) {
    actions.executeJS(function () {
        if (document.querySelector('.skin-greeting')) {
            $('.skin-greeting').bem('skin-greeting')._show();
        }
    });
}

function hideSkinGreetingPopup(actions) {
    actions.executeJS(function () {
        if (document.querySelector('.skin-greeting')) {
            $('.skin-greeting').bem('skin-greeting')._hide();
        }
    });
}

function setOverlayBackgroundColor(actions) {
    actions.executeJS(function () {
        document.querySelector('.mini-suggest__overlay-index').style.backgroundColor = '#4eb0da';
    });
}

function enchantFunc(window) {
    window._origRequest = window._origRequest || window.MBEM.blocks['mini-suggest'].prototype._request;

    window.MBEM.blocks['mini-suggest'].prototype._request = function (requestedVal) {
        if (requestedVal === replacedVal) {
            var self = this;

            setTimeout(function () {
                self._onSuggestData(response);
            }, 0);
        } else {
            window._origRequest.apply(this, arguments);
        }
    };
}

function restoreFunc(window) {
    window.MBEM.blocks['mini-suggest'].prototype._request = window._origRequest ||
        window.MBEM.blocks['mini-suggest'].prototype._request;
}

function enchantRequests(actions) {
    actions.fakeRequest = function (val, response) {
        return actions.executeJS(
            eval('(' +
                enchantFunc
                    .toString()
                    .replace(/replacedVal/g, JSON.stringify(val))
                    .replace(/response/g, JSON.stringify(response)) +
                ')')
        );
    };

    actions.restoreRequest = function () {
        return actions.executeJS(restoreFunc);
    };
}

function stopZoomFbComtr(actions) {
    actions.executeJS(function () {
        var fbBg = document.querySelector('.football-face');
        if (fbBg) {
            fbBg.classList.remove('football-face_animated_yes');
        }
    });
}

function cleatLs(actions) {
    actions.executeJS(function () {
        localStorage.clear();
    });
}

function hideDistPopup(actions) {
    actions.executeJS(function () {
        var popup = document.querySelector('.dist-popup');
        if (popup) {
            popup.style.visibility = 'hidden';
        }
    });
}

function hideResetPopup(actions) {
    actions.executeJS(function () {
        var popup = document.querySelector('.reset__popup');
        if (popup) {
            popup.style.visibility = 'hidden';
        }
    });
}

function hideArrowPromo(actions) {
    actions.executeJS(function () {
        document.querySelector('.home-arrow__promo-wrapper').style.visibility = 'hidden';
    });
}

function hideTeaser(actions) {
    actions.executeJS(function () {
        document.querySelector('.widgets__col_td_2').style.visibility = 'hidden';
    });
}

function showComtrFbSetPopup(actions) {
    actions.executeJS(function () {
        $('.reset').bem('reset').findBlockOn($('.reset__popup'), 'popup').show($('.reset').bem('reset'));
        document.querySelector('.reset__popup').style.backgroundColor = 'black';
    });
}

function strongSuggestOverlay(actions) {
    actions.executeJS(function () {
        document.querySelector('.mini-suggest__overlay-index').style.backgroundColor = '#4eb0da';
    });
}

function footerCollapse(actions) {
    actions.executeJS(function () {
        document.querySelector('.b-line__infinity-zen').classList.add('b-line_collapsed_yes')
    });
}

function hideMediaFooter(actions) {
    actions.executeJS(function () {
        $('.media-grid').bem('media-grid').setMod('collapsed', 'yes');
    });
}

function showMediaFooter(actions) {
    actions.executeJS(function () {
        document.querySelector('.media-infinity-footer__content').classList.add('media-infinity-footer__content_visible_yes');
    });
}

function mapPaint(actions) {
    actions.executeJS(function () {
        document.querySelector('ymaps>ymaps>ymaps>ymaps').style.backgroundColor = '#4eb0da';
    });
}

function cleanTouchHeader(actions) {
    actions.executeJS(function () {
        $('.mlogo__container').detach();
        $('.mheader3').detach();
        $('.body__topblocks').detach();
        document.querySelector('.content.i-bem div:nth-child(1)').remove()
    });
}

function strongParanja(actions) {
    actions.executeJS(function () {
        document.querySelector('.dialog__overlay').style.backgroundColor = '#4eb0da';
    });
}

function hideThemesPromo(actions) {
    actions.executeJS(function () {
        $('.themes-promo').bem('themes-promo')._hide();
    });
}

function setFont(actions) {
    actions.executeJS(function () {
        document.body.style.fontFamily = 'Helvetica Neue, Arial, sans-serif';
    });
}

function inputClear(actions) {
    actions.executeJS(function () {
        document.querySelector('.mini-suggest__input').value = '';
    });
}

function setFontV14(actions) {
    actions.executeJS(function () {
        document.querySelector('body').style.font ='81.25% Arial,Helvetica,sans-serif';
    });
}


module.exports.enchantRequests = enchantRequests;
module.exports.restoreFunc = restoreFunc;
module.exports.enchantFunc = enchantFunc;
module.exports.stopScroll = stopScroll;
module.exports.enableScroll = enableScroll;
module.exports.setTvBackgroundColor = setTvBackgroundColor;
module.exports.clearSuggestMiniInput = clearSuggestMiniInput;
module.exports.setHeigthInput = setHeigthInput;
module.exports.showSkinGreetingPopup = showSkinGreetingPopup;
module.exports.hideSkinGreetingPopup = hideSkinGreetingPopup;
module.exports.scrollToArrow = scrollToArrow;
module.exports.setOverlayBackgroundColor = setOverlayBackgroundColor;
module.exports.stopZoomFbComtr = stopZoomFbComtr;
module.exports.cleatLs = cleatLs;
module.exports.hideDistPopup = hideDistPopup;
module.exports.hideResetPopup = hideResetPopup;
module.exports.hideArrowPromo = hideArrowPromo;
module.exports.hideTeaser = hideTeaser;
module.exports.showComtrFbSetPopup = showComtrFbSetPopup;
module.exports.hideMediaFooter = hideMediaFooter;
module.exports.showMediaFooter = showMediaFooter;
module.exports.mapPaint = mapPaint;
module.exports.cleanTouchHeader = cleanTouchHeader;
module.exports.strongParanja = strongParanja;
module.exports.strongSuggestOverlay = strongSuggestOverlay;
module.exports.hideThemesPromo = hideThemesPromo;
module.exports.footerCollapse = footerCollapse;
module.exports.setFont = setFont;
module.exports.inputClear = inputClear;
module.exports.setFontV14 = setFontV14;
