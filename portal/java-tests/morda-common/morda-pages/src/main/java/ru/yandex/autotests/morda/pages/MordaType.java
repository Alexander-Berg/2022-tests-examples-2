package ru.yandex.autotests.morda.pages;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static ru.yandex.autotests.morda.pages.MordaContent.BIG;
import static ru.yandex.autotests.morda.pages.MordaContent.COM;
import static ru.yandex.autotests.morda.pages.MordaContent.COMTR;
import static ru.yandex.autotests.morda.pages.MordaContent.COMTRFOOT;
import static ru.yandex.autotests.morda.pages.MordaContent.FIREFOX;
import static ru.yandex.autotests.morda.pages.MordaContent.HW;
import static ru.yandex.autotests.morda.pages.MordaContent.MOB;
import static ru.yandex.autotests.morda.pages.MordaContent.OPANEL;
import static ru.yandex.autotests.morda.pages.MordaContent.TABLET;
import static ru.yandex.autotests.morda.pages.MordaContent.TEL;
import static ru.yandex.autotests.morda.pages.MordaContent.TOUCH;
import static ru.yandex.autotests.morda.pages.MordaContent.TUNE;
import static ru.yandex.autotests.morda.pages.MordaContent.TV;
import static ru.yandex.autotests.morda.pages.MordaContent.YARU;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/04/15
 */
public enum MordaType {

//    ** BIG **

    DESKTOP_COM(COM),
    DESKTOP_COMTR(COMTR),
    DESKTOP_COMTR_ALL(COMTR),
    DESKTOP_COMTR_FOOTBALL(COMTRFOOT),
    DESKTOP_FIREFOX(FIREFOX),
    DESKTOP_HW_BMW(HW),
    DESKTOP_HW_LG(HW),
    DESKTOP_HW_LG_2(BIG),
    DESKTOP_MAIN(BIG),
    DESKTOP_MAIN_ALL(BIG),
    DESKTOP_MAIN_404(BIG),
    DESKTOP_COM_404(COM),
    DESKTOP_YARU(YARU),
    D_OP(OPANEL),

//    ** MOB **

    PDA_COM(COM),
    PDA_COMTR(MOB),
    PDA_COMTR_ALL(MOB),
    PDA_MAIN(MOB),
    PDA_MAIN_ALL(MOB),
    PDA_YARU(YARU),

//    ** TOUCH **

    TOUCH_COM(COM),
    TOUCH_COMTR(TOUCH),
    TOUCH_COMTR_ALL(TOUCH),
    TOUCH_COMTR_WP(TOUCH),
    TOUCH_MAIN(TOUCH),
    TOUCH_MAIN_ALL(TOUCH),
    TOUCH_MAIN_WP(TOUCH),
    TOUCH_YARU(YARU),

//    ** TV **

    TV_SMART(TV),

//    ** TEL **

    TEL_MAIN(TEL),

//    ** TABLET **

    TABLET_MAIN(TABLET),

    //    ** TUNE **

    TOUCH_COM_TUNE(TUNE),
    TOUCH_COMTR_TUNE(TUNE),
    TOUCH_TUNE(TUNE);

    private MordaContent content;

    MordaType(MordaContent content) {
        this.content = content;
    }

    public static MordaContent fromString(String str) {
        for (MordaContent content : MordaContent.values()) {
            if (content.name().equalsIgnoreCase(str)) {
                return content;
            }
        }
        return null;
    }

    public static Set<MordaContent> contents(List<String> contents) {
        Set<MordaContent> result = new HashSet<>();

        contents.forEach(content -> {
            MordaContent c = fromString(content);
            if (c != null) {
                result.add(c);
            }
        });

        return result;
    }

    public MordaContent getContent() {
        return content;
    }

    @Override
    public String toString() {
        return name().toLowerCase();
    }
}
