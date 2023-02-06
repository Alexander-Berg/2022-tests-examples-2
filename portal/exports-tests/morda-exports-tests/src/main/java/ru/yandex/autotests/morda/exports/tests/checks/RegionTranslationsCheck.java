package ru.yandex.autotests.morda.exports.tests.checks;

import ru.yandex.autotests.morda.exports.MordaExport;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithGeoAndLang;

import java.util.List;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.exports.filters.MordaExportFilters.geo;
import static ru.yandex.autotests.morda.exports.filters.MordaExportFilters.lang;

/**
 * User: asamar
 * Date: 17.08.2015.
 */
public class RegionTranslationsCheck<T extends MordaExport<T, E>, E extends EntryWithGeoAndLang> extends ExportCheck<T> {

    private RegionTranslationsCheck(String name, List<String> langs) {
        super(
                format("\"%s\" translations", name),
                e -> checkTranslations(e, langs)
        );
    }

    public static <T extends MordaExport<T, E>, E extends EntryWithGeoAndLang>
    RegionTranslationsCheck<T, E> regionTranslationsChek(String name, List<String> langs) {
        return new RegionTranslationsCheck<>(name, langs);
    }

    private static <T extends MordaExport<T, E>, E extends EntryWithGeoAndLang>
    void checkTranslations(MordaExport<T, E> export, List<String> langs) {
        assertThat(export.getData(), hasSize(greaterThan(0)));

        export.getData().stream()
                .map(EntryWithGeoAndLang::getGeo)
                .distinct()
                .forEach(geo -> checkRegionTranslations(export, geo, langs));
    }

    private static <T extends MordaExport<T, E>, E extends EntryWithGeoAndLang>
    void checkRegionTranslations(MordaExport<T, E> export, int geo, List<String> langs) {
        langs.forEach(lang -> checkRegionTranslation(export, geo, lang));
    }

    private static <T extends MordaExport<T, E>, E extends EntryWithGeoAndLang>
    void checkRegionTranslation(MordaExport<T, E> export, int geo, String lang) {
        assertThat("Для региона " + geo + " и языка " + lang + " нет подписи",
                export.find(geo(geo), lang(lang)), hasSize(greaterThan(0)));
    }
}
