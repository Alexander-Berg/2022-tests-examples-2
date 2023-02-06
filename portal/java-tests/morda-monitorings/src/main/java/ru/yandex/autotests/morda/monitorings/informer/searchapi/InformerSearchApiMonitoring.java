package ru.yandex.autotests.morda.monitorings.informer.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.informer.InformerApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.informer.InformerApiV1Item;
import ru.yandex.autotests.morda.beans.api.search.v1.informer.InformerApiV1ItemN;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.INFORMER;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.INFORMER_REGIONS;

/**
 * User: asamar
 * Date: 27.06.16
 */
@Aqua.Test(title = "Informer search api monitoring")
@Features({"Search-api", "Informer"})
@RunWith(Parameterized.class)
public class InformerSearchApiMonitoring extends BaseSearchApiMonitoring<InformerApiV1> {
    private InformerApiV1 informers;

    public InformerSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        INFORMER_REGIONS.forEach(region -> data.add(DesktopMainMorda.desktopMain().region(region)));

        return data;
    }

    @Override
    protected InformerApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();
        informers = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.INFORMER)
                .withGeo(morda.getRegion())
                .read()
                .getInformer();

        return informers;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return INFORMER;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();

        names.addAll(informers.getData().getList().stream()
                .filter(e -> e.getN() == null)
                .map(InformerApiV1Item::getText)
                .collect(toList()));

        names.addAll(informers.getData().getMore().getList().stream()
                .map(InformerApiV1Item::getText)
                .collect(toList()));

        names.add(informers.getData().getMore().getText());

        List<InformerApiV1ItemN> itemsWithN = informers.getData().getList().stream()
                .filter(e -> e.getN() != null)
                .map(InformerApiV1Item::getN)
                .collect(toList());


        itemsWithN.forEach(n ->
//                assertThat("У n должно быть value", n, withValue(allOf(lessThan(58), greaterThan(-89))))
                        names.add(String.valueOf(n.getValue()))
        );

        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        //урлы
        urls.addAll(informers.getData().getList().stream()
                .map(InformerApiV1Item::getUrl)
                .filter(e -> e != null && !e.startsWith("intent") && !e.startsWith("viewport"))
                .collect(toList()));

        urls.addAll(informers.getData().getMore().getList().stream()
                .map(InformerApiV1Item::getUrl)
                .filter(e -> e != null && !e.startsWith("intent") && !e.startsWith("viewport"))
                .collect(toList()));

        if (informers.getData().getTraffic() != null) {
            urls.add(informers.getData().getTraffic().getUrl());
            urls.add(informers.getData().getTraffic().getMapUrl());
        }

        //иконки
        urls.addAll(informers.getData().getList().stream()
                .map(InformerApiV1Item::getIcon)
                .collect(toList()));

        urls.addAll(informers.getData().getMore().getList().stream()
                .map(InformerApiV1Item::getIcon)
                .collect(toList()));

        urls.add(informers.getData().getMore().getIcon());

        if (informers.getData().getTraffic() != null) {
            urls.add(informers.getData().getTraffic().getIcon());
        }

        return urls;
    }
}
