package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.language.TankerManager;
import ru.yandex.autotests.utils.morda.region.Region;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.HeadSettings.ADD_NEW_WIDGET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.HeadSettings.CANCEL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.HeadSettings.RESET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.HeadSettings.SAVE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.HeadSettings.UNDO_TEXT;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;

/**
 * User: alex89
 * Date: 10.07.12
 */
public class WidgetHeaderData {
    private static final Properties CONFIG = new Properties();

    private static final String SPACE = " ";
    private static final String DOUBLE_SPACE = "  ";
    public static final Region TEST_REGION = SANKT_PETERBURG;

    public static final Matcher<String> SAVE_TEXT = equalTo(getTranslation(TankerManager.TRIM, SAVE, CONFIG.getLang()));
    public static final Matcher<String> CANCEL_TEXT = equalTo(getTranslation(CANCEL, CONFIG.getLang()));
    public static final Matcher<String> RESET_TEXT =
            equalTo(getTranslation(TankerManager.TRIM, RESET, CONFIG.getLang()));
    public static final Matcher<String> UNDO_TEXT_MATCHER = equalTo(getTranslation(UNDO_TEXT, CONFIG.getLang()));
    public static final Matcher<String> ADD_WIDGET_TEXT = equalTo(getTranslation(ADD_NEW_WIDGET, CONFIG.getLang()));
}

