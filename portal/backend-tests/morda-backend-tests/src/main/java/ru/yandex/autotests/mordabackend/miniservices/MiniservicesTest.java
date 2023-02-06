package ru.yandex.autotests.mordabackend.miniservices;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.miniservices.Direct;
import ru.yandex.autotests.mordabackend.beans.miniservices.Miniservices;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.DirectV12Entry;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.selectFirst;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MINISERVICES;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.DIRECT_V12;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.mordaexportslib.matchers.MordatypeMatcher.mordatype;
import static ru.yandex.autotests.mordaexportslib.matchers.ServicesV122EntryMatcher.with;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23.07.14
 */
@Aqua.Test(title = "Miniservices")
@Features("Miniservices")
@Stories("Miniservices")
@RunWith(CleanvarsParametrizedRunner.class)
public class MiniservicesTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY)
                    .withLanguages(Language.RU, Language.UK, Language.KK, Language.TT, Language.BE)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(MINISERVICES);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final Language language;
    private final UserAgent userAgent;
    private ServicesV122Entry metrika;
    private ServicesV122Entry sprav;
    private DirectV12Entry direct;
    private ServicesV122Entry directServicesV12Entry;

    public MiniservicesTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                            Language language, UserAgent ua) {
        this.client = client;
        this.region = region;
        this.userAgent = ua;
        this.cleanvars = cleanvars;
        this.language = language;
    }

    @Before
    public void setUp() {
        metrika = export(SERVICES_V12_2, domain(region.getDomain()), with().id("metrika"));
        sprav = export(SERVICES_V12_2, domain(region.getDomain()), with().id("sprav"));
        direct = selectFirst(exports(DIRECT_V12, mordatype(region.getDomain()), lang(language)),
                having(on(DirectV12Entry.class).getLinkid(),
                        equalTo(cleanvars.getMiniservices().getDirect().getLinkid()))
        );
        directServicesV12Entry = export(SERVICES_V12_2, domain(region.getDomain()), with().id("direct"));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getMiniservices(), having(on(Miniservices.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getMiniservices(), having(on(Miniservices.class).getProcessed(), equalTo(1)));
    }

    @Test
    public void metrikaHref() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices(), having(on(Miniservices.class).getMetrika().getHref(),
                startsWith(metrika.getHref())));
        addLink(cleanvars.getMiniservices().getMetrika().getHref(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getMetrika().getHref(), equalTo(200));
    }

    @Test
    public void metrikaUrl() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices(), having(on(Miniservices.class).getMetrika().getUrl(),
                startsWith(metrika.getHref())));
    }

    @Test
    public void spravHref() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices(), having(on(Miniservices.class).getSprav().getHref(),
                equalTo(sprav.getHref())));
        addLink(cleanvars.getMiniservices().getSprav().getHref(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getSprav().getHref(), equalTo(200));
    }

    @Test
    public void spravUrl() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices(), having(on(Miniservices.class).getSprav().getUrl(),
                equalTo(sprav.getHref())));
    }

    @Test
    public void directHref() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getHref(),
            equalTo(direct.getHref())));
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getDirect().getHref(), equalTo(200));
    }

    @Test
    public void directUrl() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getUrl(),
                equalTo(directServicesV12Entry.getHref())));
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getDirect().getUrl(), equalTo(200));
    }

    @Test
    public void directShowParameter() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getShow(), equalTo(1)));
    }

    @Test
    public void directSubhref() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getSubhref(),
                equalTo(direct.getSubhref().replace("&", "&amp;"))));
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getDirect().getSubhref(), equalTo(200));
    }

    @Test
    public void directSubtitle() throws IOException {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getSubtitle(),
                equalTo(direct.getSubtitle())));
    }

}
