package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.language.Language;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * User: leonsabr
 * Date: 24.04.12
 */
public class VirtualKeyboardData {
    private static final Properties CONFIG = new Properties();

    private static final Map<Language, String> LANGUAGES = new HashMap<Language, String>() {{
        put(Language.RU, "Русский");
        put(Language.TT, "Татарча");
        put(Language.UK, "Українська");
        put(Language.KK, "Қазақша");
        put(Language.BE, "Беларуская");
    }};

    public static final Matcher<String> LANGUAGE = equalTo(LANGUAGES.get(CONFIG.getLang()));
    public static final int TEXT_LENGTH = 30;
    public static final int TOTAL_BUTTONS = 44;

    public static final Map<String, Matcher<String>> LANGUAGE_SWITCHER = new HashMap<String, Matcher<String>>() {{
        put("Татарча", matches("[һ1234567890\\-=йөукенгшәзхүъ!фывапролдңэячсмитҗбю,.]*"));
        put("Беларуская", matches("[ё1234567890\\-=йцукенгшўзх'\\\\«фывапролджэ!ячсмітьбю,.]*"));
        put("English", matches("[`1234567890\\-=qwertyuiop\\[\\]\\\\“asdfghjkl;'!zxcvbnm,.:/]*"));
        put("Français", matches("[`1234567890\\-=qwertyuiopé!asdfghjkl;'zxcvbnm,.çœ]*"));
        put("Deutsch", matches("[`1234567890\\-=qwertyuiopüä\\\\«asdfghjkl;ö!zxcvbnm,.ß]*"));
        put("Italiano", matches("[`1234567890\\-=qwertyuiop—«asdfghjkl;'!zxcvbnm,.:/]*"));
        put("Қазақша", matches("[1234567890\\-=йңукенгшғзхұ\\\\«өықапролджә!яісмитүбю,.]*"));
        put("Español", matches("[\\\\1234567890\\-=qwertyuiopü\\\\“asdfghjkl;ñ—zxcvbnm,.?!]*"));
        put("Русский", matches("[ё1234567890\\-=йцукенгшщзхъ\\\\«фывапролджэ!ячсмитьбю,.]*"));
        put("Türkçe", matches("[`1234567890\\-=qwertyuıopğü\\\\asdfghjklşi!zxcvbnmöç,.]*"));
        put("Українська", matches("['1234567890\\-=йцукенгшщзхї\\\\!фівапролджєґячсмитьбю,.]*"));
        put("Indonesian", matches("[`1234567890\\-=qwertyuiop\\[\\]\\\\“asdfghjkl;'!zxcvbnm,.:/]*"));
    }};
}
