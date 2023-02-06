package ru.yandex.autotests.mordabackend.afisha;

import org.junit.Ignore;
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

import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.*;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.AFISHA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 18.07.2014
 */
@Aqua.Test(title = "Afisha Events")
@Features("Afisha")
@Stories("Afisha Events")
@RunWith(CleanvarsParametrizedRunner.class)
public class AfishaEventLinksTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(AFISHA_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34, PDA)
                    .withCleanvarsBlocks(AFISHA);

    private final Client client;
    private Language language;
    private UserAgent userAgent;
    private String afishaHref;
    private List<AfishaEvent> events = new ArrayList<>();
    private int noPremiereEventCount;

    public AfishaEventLinksTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                                Region region, Language language, UserAgent userAgent) {
        this.client = client;
        this.language = language;
        this.userAgent = userAgent;
        this.afishaHref = getAfishaHref(userAgent, region);
        this.noPremiereEventCount = cleanvars.getAfisha().getEvents().size();
        this.events.addAll(cleanvars.getAfisha().getEvents());
        if (cleanvars.getAfisha().getPremiere() != null) {
            this.events.add(cleanvars.getAfisha().getPremiere());
        }
    }

    @Test
    public void afishaEventLinks() throws IOException {
        for (AfishaEvent event : events) {
            shouldHaveEventLink(event.getName(), event, client, userAgent, afishaHref);
        }
    }

    @Test
    public void afishaEventTexts() {
        for (AfishaEvent event : events) {
            shouldHaveEvent(event.getName(), event, language, noPremiereEventCount, userAgent);
        }
    }

    @Test
    @Ignore
    public void afishaEventPosters() throws IOException {
        for (AfishaEvent event : events) {
            shouldHaveEventPosters(event.getName(), event, client, userAgent);
        }
    }
}
