package ru.yandex.autotests.mordabackend.mobile.afisha;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaEvent;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.shouldHaveEvent;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.shouldHaveEventLink;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.shouldHaveEventPosters;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.AFISHA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 18.07.2014
 */
@Aqua.Test(title = "Afisha New Touch Events")
@Features("Mobile")
@Stories("Afisha New Touch Events")
@RunWith(CleanvarsParametrizedRunner.class)
public class AfishaNewTouchEventLinksTest {

    private static final String AFISHA_HREF = "https://afisha.yandex.ru/";

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(Region.MOSCOW)
                    .withLanguages(Language.RU)
                    .withUserAgents(TOUCH)
                    .withCleanvarsBlocks(AFISHA);

    private final Client client;
    private Language language;
    private UserAgent userAgent;
    private List<AfishaEvent> events;
    private int noPremiereEventCount;

    public AfishaNewTouchEventLinksTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                                        Region region, Language language, UserAgent userAgent) {
        this.client = MordaClient.getJsonEnabledClient();
        this.language = language;
        this.userAgent = userAgent;
        this.noPremiereEventCount = cleanvars.getAfisha().getEvents().size();
        this.events = new ArrayList<>();
        this.events.addAll(cleanvars.getAfisha().getEvents());
        if (cleanvars.getAfisha().getPremiere() != null) {
            this.events.add(cleanvars.getAfisha().getPremiere());
        }
    }

    @Test
    public void afishaEventLinks() throws IOException {
        for (AfishaEvent event : events) {
            shouldHaveEventLink(event.getName(), event, client, userAgent, AFISHA_HREF);
        }
    }

    @Test
    public void afishaEventTexts() {
        for (AfishaEvent event : events) {
            shouldHaveEvent(event.getName(), event, language, noPremiereEventCount, userAgent);
        }
    }

    @Test
    public void afishaEventPosters() throws IOException {
        for (AfishaEvent event : events) {
            shouldHaveEventPosters(event.getName(), event, client, userAgent);
        }
    }
}
