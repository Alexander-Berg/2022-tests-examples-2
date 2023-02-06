package ru.yandex.autotests.morda.pages.hw;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;

import java.net.URI;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20/07/16
 */
public abstract class HwMorda<T> extends AbstractMorda<T> implements MordaWithRegion<T> {

    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.RU));
    private static final URI PASSPORT_HOST = URI.create("https://passport.yandex.ru/");
    private static final URI TUNE_HOST = URI.create("https://tune.yandex.ru/");

    protected HwMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        language(MordaLanguage.RU);
        region(Russia.MOSCOW);
    }

    public static List<HwMorda<?>> getDefaultHwList(String environment) {
        List<HwMorda<?>> data = new ArrayList<>();
        data.addAll(DesktopHwLgMorda.getDefaultList(environment));
        data.addAll(DesktopHwBmwMorda.getDefaultList(environment));
        data.addAll(DesktopHwLgV2Morda.getDefaultList(environment));
        return data;
    }

    @Override
    public URI getPassportHost() {
        return PASSPORT_HOST;
    }

    @Override
    public URI getTuneHost() {
        return TUNE_HOST;
    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.RU;
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public GeobaseRegion getRegion() {
        return super.getRegion();
    }

    @Override
    public T region(GeobaseRegion region) {
        return super.region(region);
    }

    @Override
    public String toString() {
        return super.toString() + " " + getRegion();
    }
}
