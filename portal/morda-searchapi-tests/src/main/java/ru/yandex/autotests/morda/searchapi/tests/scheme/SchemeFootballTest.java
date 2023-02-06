package ru.yandex.autotests.morda.searchapi.tests.scheme;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.searchapi.client.MordaSearchApi;
import ru.yandex.autotests.morda.searchapi.tests.MordaSearchApiTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.searchapi.tests.scheme.SchemeAbstractTest.ValidationCase.validationCase;

/**
 * User: asamar
 * Date: 11.11.2015.
 */
@Aqua.Test(title = "Api Foolball Response Scheme")
@RunWith(Parameterized.class)
@Features("JSON-schema validation")
public class SchemeFootballTest extends SchemeAbstractTest {

    private static final MordaSearchApiTestsProperties CONFIG = new MordaSearchApiTestsProperties();

    public SchemeFootballTest(ValidationCase validationCase) {
        super(validationCase);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        MordaSearchApi mordaSearchApi = new MordaSearchApi(CONFIG.getMordaFootbalApiHost());
        List<Object[]> data = new ArrayList<>();

        data.add(new Object[]{
                validationCase(
                        "Football_FB",
                        mordaSearchApi.getMordaFootballApiV1Request().withFootballClub("fb"),
                        ValidateSchemeUtils.TEST_SCHEMAS.get("football")
                )
        });

        data.add(new Object[]{
                validationCase(
                        "Football_GS",
                        mordaSearchApi.getMordaFootballApiV1Request().withFootballClub("gs"),
                        ValidateSchemeUtils.TEST_SCHEMAS.get("football")
                )
        });

        data.add(new Object[]{
                validationCase(
                        "Football_BJK",
                        mordaSearchApi.getMordaFootballApiV1Request().withFootballClub("bjk"),
                        ValidateSchemeUtils.TEST_SCHEMAS.get("football")
                )
        });

        return data;
    }
}
