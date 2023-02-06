package ru.yandex.autotests.mordabackend.etrains;

import org.joda.time.DateTime;
import org.joda.time.ReadableInstant;
import org.joda.time.format.DateTimeFormat;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.etrains.EtrainItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.EtrainItemsParametrProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.ETRAINS;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HIDDENTIME;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ATBASAR;
import static ru.yandex.autotests.utils.morda.region.Region.BROVARY;
import static ru.yandex.autotests.utils.morda.region.Region.ORSHA;
import static ru.yandex.autotests.utils.morda.region.Region.VYBORG;

/**
 * User: ivannik
 * Date: 11.09.2014
 */
@Aqua.Test(title = "Etrain Items Block")
@Features("Etrains")
@Stories("Etrain Items Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class EtrainsItemsTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(VYBORG, BROVARY, ORSHA, ATBASAR)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(FF_34, TOUCH)
                    .withParameterProvider(new EtrainItemsParametrProvider())
                    .withCleanvarsBlocks(ETRAINS, HIDDENTIME);

    private final Client client;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private EtrainItem etrainItem;

    public EtrainsItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                       Region region, Language language, UserAgent userAgent, String timeStamp, EtrainItem etrainItem) {
        this.userAgent = userAgent;
        this.client = client;
        this.cleanvars = cleanvars;
        this.etrainItem = etrainItem;
    }

    @Test
    public void itemUrl() throws IOException {
        shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getUrl(), not(isEmptyOrNullString())));
        shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getUrl(), containsString(etrainItem.getUid())));
        shouldHaveResponseCode(client, normalizeUrl(etrainItem.getUrl()), userAgent, equalTo(200));
    }

    @Test
    public void itemDateTime() {
        DateTime itemTime = DateTimeFormat.forPattern("yyyyMMddHHmmss").parseDateTime(etrainItem.getTime());
        shouldMatchTo(itemTime, greaterThanOrEqualTo((ReadableInstant) DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss")
                        .parseDateTime(cleanvars.getHiddenTime())));
        shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getDate(),
                equalTo(DateTimeFormat.forPattern("yyyyMMdd").print(itemTime))));
        shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getDatesign(),
                equalTo(DateTimeFormat.forPattern("yyyy-MM-dd").print(itemTime))));
        shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getStime(),
                equalTo(DateTimeFormat.forPattern("H:mm").print(itemTime))));
    }

    @Test
    public void itemName() {
        shouldHaveParameter(etrainItem, having(on(EtrainItem.class).getName(), not(isEmptyOrNullString())));
    }
}
