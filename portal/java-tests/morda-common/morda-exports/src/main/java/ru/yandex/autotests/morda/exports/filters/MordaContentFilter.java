package ru.yandex.autotests.morda.exports.filters;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithContent;
import ru.yandex.autotests.morda.pages.MordaContent;

import java.util.Comparator;
import java.util.function.Predicate;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/06/16
 */
public enum MordaContentFilter {
    UNKNOWN("unknown"),
    ALL("all"),
    API_FOOTBALL("api_football"),
    API_SEARCH("api_search"),
    BIG("big"),
    COM("com"),
    COMTR("comtr"),
    COMTRFOOT("comtrfoot"),
    FAMILY("family"),
    FIREFOX("firefox"),
    INTERCEPT404("intercept404"),
    MOB("mob"),
    MOBYARU("mobyaru"),
    OPANEL("opanel"),
    TABLET("tablet"),
    TEL("tel"),
    TOUCH("touch"),
    TV("tv"),
    TV_1("tv_1"),
    TV_2("tv_2"),
    VOICEBRIEF("voicebrief"),
    YACOMTR("yacomtr"),
    YARU("yaru"),
    YAUA("yaua");

    private static final Logger LOGGER = Logger.getLogger(MordaContentFilter.class);

    private String value;

    MordaContentFilter(String value) {
        this.value = value;
    }

    public static MordaContentFilter fromString(String v) {
        for (MordaContentFilter filter : MordaContentFilter.values()) {
            if (filter.getValue().equalsIgnoreCase(v)) {
                return filter;
            }
        }
        LOGGER.warn("No content filter found for value " + v);
        return UNKNOWN;
    }

    public static Predicate<EntryWithContent> filter(MordaContent content) {
        return e -> e.getContent().matches(content);
    }

    public boolean matches(MordaContent content) {
        return this == ALL || this.value.equals(content.getValue());
    }

    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return value;
    }

    public static class MordaContentFilterComparator implements Comparator<EntryWithContent> {

        @Override
        public int compare(EntryWithContent e1, EntryWithContent e2) {
            MordaContentFilter c1 = e1.getContent();
            MordaContentFilter c2 = e2.getContent();

            if (c1 == UNKNOWN || c2 == UNKNOWN) {
                throw new IllegalStateException("Some filter is unknown. Can't compare");
            }

            if (c1 == c2 || (c1 != ALL && c2 != ALL)) {
                return 0;
            }

            if (c1 == ALL) {
                return -1;
            }

            return 1;
        }
    }


}
