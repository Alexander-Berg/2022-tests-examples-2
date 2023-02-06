package ru.yandex.autotests.morda.monitorings.afisha.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.afisha.AfishaApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.afisha.AfishaApiV1Event;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static ru.yandex.autotests.morda.api.search.SearchApiBlock.AFISHA;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Russia.DUBNA;
import static ru.yandex.geobase.regions.Russia.KAZAN;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;
import static ru.yandex.geobase.regions.Russia.NOVOSIBIRSK;
import static ru.yandex.geobase.regions.Russia.OMSK;
import static ru.yandex.geobase.regions.Russia.SAINT_PETERSBURG;
import static ru.yandex.geobase.regions.Russia.SAMARA;
import static ru.yandex.geobase.regions.Russia.VLADIVOSTOK;
import static ru.yandex.geobase.regions.Russia.VORONEZH;
import static ru.yandex.geobase.regions.Russia.YEKATERINBURG;
import static ru.yandex.geobase.regions.Ukraine.KHARKIV;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 27.06.16
 */
@Aqua.Test(title = "Afisha search api monitoring")
@Features({"Search-api", "Afisha"})
@RunWith(Parameterized.class)
public class AfishaSearchApiMonitoring extends BaseSearchApiMonitoring<AfishaApiV1> {
    private AfishaApiV1 afisha;

    public AfishaSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        Stream.of(MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK, VLADIVOSTOK, YEKATERINBURG,
                DUBNA, VORONEZH, OMSK, KAZAN, NIZHNY_NOVGOROD, SAMARA, KYIV, KHARKIV, MINSK)
                .forEach(region -> data.add(desktopMain(CONFIG.getEnvironment()).region(region)));

        return data;
    }

    @Override
    protected AfishaApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();
        this.afisha = mordaClient.search()
                .v1(CONFIG.getEnvironment(), AFISHA)
                .withGeo(morda.getRegion())
                .queryParam("afisha_version", "3")
                .read()
                .getAfisha();

        return afisha;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return AFISHA;
    }

    @Override
    protected List<String> getSearchApiNames() {
        return afisha.getData().getEvents().stream()
                .map(AfishaApiV1Event::getName)
                .collect(Collectors.toList());
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        urls.addAll(afisha.getData().getEvents().stream()
                .map(AfishaApiV1Event::getUrl)
                .collect(Collectors.toList()));

        urls.addAll(afisha.getData().getEvents().stream()
                .filter(e -> e.getPoster() != null && !e.getPoster().isEmpty())
                .map(AfishaApiV1Event::getPoster)
                .collect(Collectors.toList()));

        urls.add(afisha.getData().getUrl());

        return urls;
    }
}
