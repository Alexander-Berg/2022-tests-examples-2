package ru.yandex.autotests.mordabackend.afisha;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.afisha.Afisha;
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
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static java.util.Calendar.FRIDAY;
import static java.util.Calendar.MONDAY;
import static java.util.Calendar.SATURDAY;
import static java.util.Calendar.SUNDAY;
import static java.util.Calendar.THURSDAY;
import static java.util.Calendar.TUESDAY;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.AFISHA_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getNoPremiereMatcher;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getPremiereAfterTomorrowMessage;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getPremiereGenreSize;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getPremiereMessage;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getPremiereSize;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getPremiereTomorrowMessage;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.isDayIn;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.AFISHA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 03.07.2014
 */
@Aqua.Test(title = "Afisha Premiere")
@Features("Afisha")
@Stories("Afisha Premiere")
@RunWith(CleanvarsParametrizedRunner.class)
public class PremiereTest {
    private static final String PREMIERE_GENRE = "премьера";

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(AFISHA_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34, PDA)
                    .withCleanvarsBlocks(AFISHA);

    private Region region;
    private Language language;
    private Cleanvars cleanvars;

    public PremiereTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                        Region region, Language language, UserAgent userAgent) {
        this.region = region;
        this.language = language;
        this.cleanvars = cleanvars;
    }

//    @Test
    public void premiereCount() {
        shouldHaveParameter(cleanvars.getAfisha().getPremiere(),
                having(on(Afisha.class).getPremiere(), getPremiereSize()));
    }

    @Test
    public void premiereGenreCount() {
        List<AfishaEvent> premiereEvents = select(cleanvars.getAfisha().getEvents(),
                having(on(AfishaEvent.class).getGenre(), equalTo(PREMIERE_GENRE)));
        shouldMatchTo(premiereEvents, getPremiereGenreSize(region));
    }

    @Test
    public void wrongPremieresMessages() {
        String premiereMsg = getPremiereMessage(language);
        String premiereTomorrowMsg = getPremiereTomorrowMessage(language);
        String premiereAfterTomorrowMsg = getPremiereAfterTomorrowMessage(language);

        if (isDayIn(region, MONDAY, TUESDAY, SATURDAY, SUNDAY) &&
                (cleanvars.getIsHoliday() == null || cleanvars.getIsHoliday().equals("0"))) {
            shouldMatchTo(cleanvars.getAfisha().getPremiere(), getNoPremiereMatcher(premiereMsg));
        }
        if (isDayIn(region, MONDAY, FRIDAY, SATURDAY, SUNDAY) &&
                (cleanvars.getIsHoliday() == null || cleanvars.getIsHoliday().equals("0"))) {
            shouldMatchTo(cleanvars.getAfisha().getPremiere(), getNoPremiereMatcher(premiereTomorrowMsg));
        }
        if (isDayIn(region, THURSDAY, FRIDAY, SATURDAY, SUNDAY) &&
                (cleanvars.getIsHoliday() == null || cleanvars.getIsHoliday().equals("0"))) {
            shouldMatchTo(cleanvars.getAfisha().getPremiere(), getNoPremiereMatcher(premiereAfterTomorrowMsg));
        }
    }
}
