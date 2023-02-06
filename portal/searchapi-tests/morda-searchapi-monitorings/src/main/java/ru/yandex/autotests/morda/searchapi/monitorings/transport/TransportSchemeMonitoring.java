package ru.yandex.autotests.morda.searchapi.monitorings.transport;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.searchapi.client.MordaSearchApi;
import ru.yandex.autotests.morda.searchapi.monitorings.SchemeAbstractMonitoring;
import ru.yandex.autotests.morda.searchapi.tests.MordaSearchApiTestsProperties;
import ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.String.join;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.SchemeAbstractTest.ValidationCase.validationCase;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.langs;
import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.regions;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/06/15
 */
@Aqua.Test(title = "Transport Scheme")
@RunWith(Parameterized.class)
@Features("Search API Transport Scheme")
public class TransportSchemeMonitoring extends SchemeAbstractMonitoring {
    private static final MordaSearchApiTestsProperties CONFIG = new MordaSearchApiTestsProperties();
    private static final String BLOCK = "transport";

    public TransportSchemeMonitoring(ValidationCase validationCase) {
        super(validationCase);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() throws Exception {
        MordaSearchApi mordaSearchApi = new MordaSearchApi(CONFIG.getMordaSearchApiHost());
        List<Object[]> data = new ArrayList<>();

        langs.forEach(lang ->
                regions.forEach(region ->
                        data.add(new Object[]{
                                validationCase(
                                        join("_", lang, region.toString(), BLOCK),
                                        mordaSearchApi.getMordaSearchApiV1Req()
                                                .withLang(lang)
                                                .withBlock(BLOCK)
                                                .withGeoBySettings(region.getId()),
                                        ValidateSchemeUtils.TEST_SCHEMAS.get(BLOCK)
                                )
                        })));
        return data;
    }

}
