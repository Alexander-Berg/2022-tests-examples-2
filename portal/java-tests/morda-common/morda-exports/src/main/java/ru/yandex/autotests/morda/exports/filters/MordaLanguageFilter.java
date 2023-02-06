package ru.yandex.autotests.morda.exports.filters;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithLang;
import ru.yandex.autotests.morda.pages.MordaLanguage;

import java.util.function.Predicate;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/06/16
 */
public enum MordaLanguageFilter {
    UNKNOWN("unknown"),
    ALL("all"),
    RU("ru", MordaLanguage.RU),
    UA("ua", MordaLanguage.UK),
    BY("by", MordaLanguage.BE),
    KZ("kz", MordaLanguage.KK),
    TT("tt", MordaLanguage.TT),
    TR("tr", MordaLanguage.TR),
    EN("en", MordaLanguage.EN);

    private static final Logger LOGGER = Logger.getLogger(MordaLanguageFilter.class);

    private String value;
    private MordaLanguage language;

    MordaLanguageFilter(String value) {
        this.value = value;
    }

    MordaLanguageFilter(String value, MordaLanguage language) {
        this.value = value;
        this.language = language;
    }

    public static MordaLanguageFilter fromString(String v) {
        for (MordaLanguageFilter filter : MordaLanguageFilter.values()) {
            if (filter.getValue().equalsIgnoreCase(v)) {
                return filter;
            }
        }
        LOGGER.warn("No language filter found for value " + v);
        return UNKNOWN;
    }

    public static Predicate<EntryWithLang> filter(MordaLanguage language) {
        return e -> e.getLang().matches(language);
    }

    public boolean matches(MordaLanguage language) {
        return this == ALL || this.language == language;
    }

    public String getValue() {
        return value;
    }


    @Override
    public String toString() {
        return value;
    }
}
