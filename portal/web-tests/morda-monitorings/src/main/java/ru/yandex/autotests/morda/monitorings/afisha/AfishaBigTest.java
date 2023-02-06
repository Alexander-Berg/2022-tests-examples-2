package ru.yandex.autotests.morda.monitorings.afisha;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.afisha.Afisha;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaEvent;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaPremiereEvent;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.data.MordaDate;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static java.lang.String.format;
import static java.util.Calendar.FRIDAY;
import static java.util.Calendar.MONDAY;
import static java.util.Calendar.SATURDAY;
import static java.util.Calendar.SUNDAY;
import static java.util.Calendar.THURSDAY;
import static java.util.Calendar.TUESDAY;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.lessThan;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getAfishaDayOfWeek;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.getPremiereSize;
import static ru.yandex.autotests.mordabackend.afisha.AfishaUtils.isDayIn;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.AFISHA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_23;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: ivannik
 * Date: 03.07.2014
 */
@Aqua.Test(title = "Афиша, много регионов")
@Features("Афиша")
@RunWith(CleanvarsParametrizedRunner.class)
public class AfishaBigTest {

    @CleanvarsParametrizedRunner.Parameters("{3}")
    public static ParametersUtils parameters =
            parameters(AfishaData.AFISHA_REGIONS_BIG)
                    .withLanguages(Language.RU)
                    .withUserAgents(FF_23)
                    .withCleanvarsBlocks(AFISHA);

    private Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private String day;
    private List<AfishaEvent> events;
    private static final Matcher<String> PREMIERE_MESSAGE = anyOf(
            equalTo("прем'єра"),
            equalTo("премьера"));
    private static final Matcher<String> PREMIERE_TOMORROW_MESSAGE = anyOf(
            equalTo("прем'єра завтра"),
            equalTo("премьера завтра"));
    private static final Matcher<String> PREMIERE_AFTER_TOMORROW_MESSAGE = anyOf(
            equalTo("прем'єра післязавтра"),
            equalTo("премьера послезавтра"));

    public AfishaBigTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                         Region region, Language language, UserAgent userAgent) {
        this.region = region;
        this.language = language;
        this.cleanvars = cleanvars;
        this.client = client;
        this.userAgent = userAgent;
        this.events = new ArrayList<>();
        this.events.addAll(cleanvars.getAfisha().getEvents());
        this.events.add(cleanvars.getAfisha().getPremiere());
        this.day = getTranslation(MordaDate.DAY_OF_WEEK.get(getAfishaDayOfWeek(region)), Language.RU);
    }

//    @Rule
//    public BottleMessageRule bottleMessageRule = new BottleMessageRule();

    @Test
    public void premiereCount() {
        List<AfishaEvent> premiereEvents = select(cleanvars.getAfisha().getEvents(),
                having(on(AfishaEvent.class).getGenre(), PREMIERE_MESSAGE));

        System.out.println(premiereEvents.size());

        assertThat(
                format("В виджете афиши в городе %s в %s %s премьерных фильмов:\n%s", region.getName(), day,
                        premiereEvents.size(), premiereEvents),
                premiereEvents, getPremiereSize()
        );
    }

    @Test
    public void noPremiere() {
        assumeThat(isDayIn(region, MONDAY, TUESDAY, SATURDAY, SUNDAY) &&
                (cleanvars.getIsHoliday() == null || cleanvars.getIsHoliday().equals("0")), is(true));

        List<AfishaEvent> premiereEvents = select(cleanvars.getAfisha().getEvents(),
                having(on(AfishaEvent.class).getGenre(), PREMIERE_MESSAGE));

        assertThat(format("В виджете афиши премьера в городе %s в %s:\n%s", region.getName(), day,
                        premiereEvents),
                premiereEvents, hasSize(0)
        );
    }

    @Test
    public void noPremiereTomorrow() {
        assumeThat(isDayIn(region, MONDAY, FRIDAY, SATURDAY, SUNDAY) &&
                (cleanvars.getIsHoliday() == null || cleanvars.getIsHoliday().equals("0")), is(true));

        List<AfishaPremiereEvent> premiereEvents = select(cleanvars.getAfisha().getPremiere(),
                having(on(AfishaPremiereEvent.class).getPremday(), PREMIERE_TOMORROW_MESSAGE));

        assertThat(format("В виджете афиши премьера завтра в городе %s в %s:\n%s", region.getName(), day,
                        premiereEvents),
                premiereEvents, hasSize(0)
        );
    }

    @Test
    public void noPremiereAfterTomorrow() {
        assumeThat(isDayIn(region, THURSDAY, FRIDAY, SATURDAY, SUNDAY) &&
                (cleanvars.getIsHoliday() == null || cleanvars.getIsHoliday().equals("0")), is(true));

        List<AfishaPremiereEvent> premiereEvents = select(cleanvars.getAfisha().getPremiere(),
                having(on(AfishaPremiereEvent.class).getPremday(), PREMIERE_AFTER_TOMORROW_MESSAGE));

        assertThat(format("В виджете афиши премьера послезавтра в городе %s в %s:\n%s", region.getName(), day,
                        premiereEvents),
                premiereEvents, hasSize(0)
        );
    }

    @Test
    public void afishaEventLinks() throws IOException {
        for (AfishaEvent event : events) {
            shouldHaveResponseCode(format("В виджете афиши в городе %s в %s ведет на несуществующую ссылку:\n%s",
                            region.getName(), event.getFull(), event.getRawHref()),
                    client, normalizeUrl(event.getRawHref()), userAgent, lessThan(400)
            );
        }
    }

    @Test
    public void afishaWidgetIsShown() {
        shouldHaveParameter(format("Виджет афиши в городе %s в %s не показывается!", region.getName(), day),
                cleanvars.getAfisha(), having(on(Afisha.class).getShow(), equalTo(1))
        );
    }
}
