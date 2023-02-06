package ru.yandex.autotests.morda.exports.tests.checks;

import ru.yandex.autotests.morda.exports.AbstractMordaExport;
import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;
import ru.yandex.autotests.morda.exports.filters.MordaLanguageFilter;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithGeoAndLang;
import ru.yandex.autotests.morda.pages.MordaLanguage;

import java.util.List;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;

/**
 * User: asamar
 * Date: 17.08.2015.
 */
public class RegionTranslationsCheck<T extends AbstractMordaExport<T, E>, E extends EntryWithGeoAndLang> extends ExportCheck<T> {

    private RegionTranslationsCheck(String name, List<MordaLanguage> langs) {
        super(
                format("\"%s\" translations", name),
                e -> checkTranslations(e, langs)
        );
    }

    public static <T extends AbstractMordaExport<T, E>, E extends EntryWithGeoAndLang>
    RegionTranslationsCheck<T, E> regionTranslationsChek(String name, List<MordaLanguage> langs) {
        return new RegionTranslationsCheck<>(name, langs);
    }

    private static <T extends AbstractMordaExport<T, E>, E extends EntryWithGeoAndLang>
    void checkTranslations(AbstractMordaExport<T, E> export, List<MordaLanguage> langs) {
        assertThat(export.getData(), hasSize(greaterThan(0)));

        export.getData().stream()
                .map(e -> e.getGeo().getRegion().getRegionId())
                .distinct()
                .forEach(geo -> checkRegionTranslations(export, geo, langs));
    }

    private static <T extends AbstractMordaExport<T, E>, E extends EntryWithGeoAndLang>
    void checkRegionTranslations(AbstractMordaExport<T, E> export, int geo, List<MordaLanguage> langs) {
        langs.forEach(lang -> checkRegionTranslation(export, geo, lang));
    }

    private static <T extends AbstractMordaExport<T, E>, E extends EntryWithGeoAndLang>
    void checkRegionTranslation(AbstractMordaExport<T, E> export, int geo, MordaLanguage lang) {
        assertThat("Для региона " + geo + " и языка " + lang + " нет подписи",
                export.find(
                        MordaGeoFilter.filter(geo),
                        MordaLanguageFilter.filter(lang)),
                hasSize(greaterThan(0))
        );

    }
}
