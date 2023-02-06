package ru.yandex.autotests.mordabackend.services;

import ch.lambdaj.function.convert.Converter;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.servicesblock.ServicesBlockLink;
import ru.yandex.autotests.mordabackend.utils.MordaVersion;
import ru.yandex.autotests.mordabackend.utils.parameters.DefaultServicesV122ParameterProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordaexportsclient.beans.SignEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.*;
import static org.junit.Assert.assertThat;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SERVICES;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.*;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: ivannik
 * Date: 20.06.2014
 */
@Aqua.Test(title = "Default Services")
@Features("Services")
@Stories("Default Services")
@RunWith(CleanvarsParametrizedRunner.class)
public class DefaultServicesBlockTest {
    private static final Properties CONFIG = new Properties();
    public static final String WITH_COMMENT = "2";

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY)
                    .withParameterProvider(new DefaultServicesV122ParameterProvider(
                            MordaVersion.fromMordaEnv(CONFIG.getMordaEnv())))
                    .withCleanvarsBlocks(SERVICES);

    private final Client client;
    private final Cleanvars cleanvars;
    private final ServicesV122Entry expectedEntry;
    private final Region region;
    private final List<SignEntry> signs;
    private ServicesBlockLink servicesBlockLink;

    public DefaultServicesBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                     String service, ServicesV122Entry expectedEntry, List<SignEntry> signs) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.expectedEntry = expectedEntry;
        this.region = region;
        this.signs = signs;
    }

    @Before
    public void setUp() {
        List<ServicesBlockLink> allServices = new ArrayList<>();
        allServices.addAll(cleanvars.getServices().getHash().get(WITH_COMMENT));
        servicesBlockLink = selectFirst(allServices, having(on(ServicesBlockLink.class).getId(),
                equalTo(expectedEntry.getId())));
        assumeThat("Сервис " + expectedEntry.getId() + " не пришел", servicesBlockLink, notNullValue());
    }

    @Test
    public void serviceType() {
        shouldMatchTo(servicesBlockLink,
                having(on(ServicesBlockLink.class).getType(), equalTo(WITH_COMMENT)));
    }

    @Test
    public void serviceUrl() throws IOException, URISyntaxException {
        shouldHaveParameter(servicesBlockLink, having(on(ServicesBlockLink.class).getUrl(), notNullValue()));
        String uri = normalizeUrl(servicesBlockLink.getUrl());
        String host = new URI(uri).getHost();
        if("autoru".equals(expectedEntry.getId())){
            shouldMatchTo("Домен неверный", host, endsWith("auto.ru"));
        } else if("avia".equals(expectedEntry.getId())){
            if (UA.equals(region.getDomain())) {
                shouldMatchTo("Домен неверный", host, endsWith(expectedEntry.getDomain()));
            } else {
                shouldMatchTo("Домен неверный", host, endsWith("avia.yandex.ru"));
            }
        }else {
            shouldMatchTo("Домен неверный", host, endsWith(expectedEntry.getDomain()));
        }
        shouldHaveResponseCode(client, uri, lessThan(400));
    }

    @Test
    public void serviceCommentText() {
        assertThat(servicesBlockLink.getText().replace("\u00A0", " "),
                isIn(convert(signs, new Converter<SignEntry, String>() {
                    @Override
                    public String convert(SignEntry from) {
                        return from.getText().replace("\u00A0", " ");
                    }})));
    }

    @Test
    public void serviceCommentUrl() throws IOException {
        shouldHaveParameter(servicesBlockLink, having(on(ServicesBlockLink.class).getUrltext(),
                isIn(extract(signs, on(SignEntry.class).getUrltext()))));
        String url = normalizeUrl(servicesBlockLink.getUrltext()).replace("|", "%7C");
        shouldHaveResponseCode(client, url, lessThan(400));
    }
}
