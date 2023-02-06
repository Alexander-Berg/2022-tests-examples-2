package ru.yandex.autotests.mordabackend.direct;

import ch.lambdaj.function.convert.Converter;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.miniservices.Direct;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.DirectV12Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isIn;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MINISERVICES;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.DIRECT_V12;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.mordaexportslib.matchers.MordatypeMatcher.mordatype;


/**
 * User: ivannik
 * Date: 09.07.2014
 */
@Aqua.Test(title = "Direct Block")
@Features("Direct")
@Stories("Direct Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class DirectBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(Domain.RU, Domain.UA, Domain.BY, Domain.KZ)
                    .withLanguages(Language.RU, Language.UK, Language.BE, Language.KK, Language.TT)
                    .withCleanvarsBlocks(MINISERVICES);


    private Client client;
    private Cleanvars cleanvars;
    private List<DirectV12Entry> directExports;

    public DirectBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                           Region region, Language language) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.directExports = exports(DIRECT_V12, mordatype(region.getDomain()), lang(language));
    }

    @Test
    public void linkid() {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getLinkid(),
                isIn(extract(directExports, on(DirectV12Entry.class).getLinkid()))));
    }

    @Test
    public void subtitle() {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getSubtitle(),
                isIn(extract(directExports, on(DirectV12Entry.class).getSubtitle()))));
    }

    @Test
    public void href() throws IOException {
        List<String> expectedRawHrefs = extract(directExports, on(DirectV12Entry.class).getHref());

        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getHref(), isIn(expectedRawHrefs)));
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getDirect().getHref(), equalTo(200));

        List<String> processedHrefs = convert(expectedRawHrefs, new Converter<String, String>() {
            @Override
            public String convert(String from) {
                return from.replace("&", "&amp;");
            }
        });

        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getHref(), isIn(processedHrefs)));
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getDirect().getHref(), equalTo(200));
    }

    @Test
    public void subhref() throws IOException {
        List<String> expectedRawSubhrefs = extract(directExports, on(DirectV12Entry.class).getSubhref());

        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getSubhref(), isIn(expectedRawSubhrefs)));
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getDirect().getSubhref(), equalTo(200));

        List<String> processedSubhrefs = convert(expectedRawSubhrefs, new Converter<String, String>() {
            @Override
            public String convert(String from) {
                return from.replace("&", "&amp;");
            }
        });

        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getSubhref(), isIn(processedSubhrefs)));
        shouldHaveResponseCode(client, cleanvars.getMiniservices().getDirect().getSubhref(), equalTo(200));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getShow(), equalTo(1)));
    }

//    @Test
    public void processedFlag() {
//        shouldHaveParameter(cleanvars.getMiniservices().getDirect(), having(on(Direct.class).getProcessed(), equalTo(1)));
    }
}
