package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractTabletMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.geobase.regions.Russia;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TabletMainMorda extends MainMorda<TabletMainMorda>
        implements AbstractTabletMorda<TabletMainMorda> {

    private TabletMainMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        experiments("media_white");
    }

    public static TabletMainMorda tabletMain() {
        return tabletMain("production");
    }

    public static TabletMainMorda tabletMain(String environment) {
        return tabletMain("https", environment);
    }

    public static TabletMainMorda tabletMain(String scheme, String environment) {
        return new TabletMainMorda(scheme, "www", environment);
    }

    public static List<TabletMainMorda> getDefaultList(String environment) {
        return asList(
                tabletMain(environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                tabletMain(environment).region(Russia.SAINT_PETERSBURG).language(MordaLanguage.UK)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TABLET_MAIN;
    }

//    @Override
//    public URI getUrl() {
//        return UriBuilder.fromUri(super.getUrl()).queryParam("content", "tablet").build();
//    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.RU;
    }

    @Override
    public TabletMainMorda me() {
        return this;
    }
}
