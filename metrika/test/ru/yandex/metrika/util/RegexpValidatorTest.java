package ru.yandex.metrika.util;

import java.util.Arrays;
import java.util.Collection;

import junit.framework.TestCase;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

@RunWith(Parameterized.class)
public class RegexpValidatorTest extends TestCase {
    @Parameterized.Parameter
    public String name;
    @Parameterized.Parameter(1)
    public String checkPhrase;
    @Parameterized.Parameter(2)
    public boolean isValid;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return Arrays.asList(
                new Object[][]{{
                        "METRIKASUPP-13410- Valid #1",
                        "domcli|dom (cli|kli)|domkli|домклик|вщьсд|вщь (сдш|лдш)|вщьлд|ljvrk|ljv rkb|" +
                                "sber|c,th|сбер|ыиук|клик дом|домкл(е|и|к|мк|тк)|дом\\+клик|" +
                                "домо(клик|лик|линк)|доклик|дом.(клие|клик)|домкоик|домлик|доиклик|кликдом" +
                                "|домулик|дом ( елик|крик|колик|коик|кик|кли|клмк|линк|кдик|\\-клик|улик|" +
                                "лик|кклик|клк|клтк|комк|лик|слик)|до клик|домкдик|домкик|дос клик|domoclick|" +
                                "domcklick|дои клик|длмклик|dom\\.(click|clik)|dom(\\-click|ckick)|" +
                                "дмклик|досклик| домелик|омклик|дрмклик|домлкик|длм клик|domoklik|" +
                                "(док|дон) клик|докклик|долмклик|дом click\\.ru|дом\\.клик\\.ру|дома клик|" +
                                "домаклик|домалик|домик клик|домиклик|домк (клик|лик)|домкилик|домкилк|" +
                                "дом-клик|домулмк| ^клик$|^клик ру$|bom klik|click dom|clickdom|dimclick|" +
                                "dom( кли|\\.cli|\\.kli|clo|cli|lik|link|lic)|клик|domcklik|domolink|домкл|" +
                                "домлин|^домк$|8007709999|770-99-99|click|rkbr|dom|ljvkbr|домrkbr|ljbrkbr|" +
                                "ljbrkbr|rkbrljv|домик ру|jvrkbr|rkbr he|^дом кл$|дом(слик|елик|комк)|" +
                                "^дом к$|партнер|партнег|домк партне|партнёр|парлайн|парнер|ljvr",
                        true
                }, {
                        "METRIKASUPP-13410- Valid #2",
                        "\\/otvet\\/d{3}-1-0-1\\d{4}$",
                        true
                }, {
                        "METR-43773 - Valid #1",
                        "дом\\sкофе|кофе\\\\дом|domcof|domkof|dom kof|coffeedom|cofedom|домкофе|кофедом|ljv rjat|\\.ru|\\.ру",
                        true
                }, {
                        "METR-43773 - InValid #1",
                        "дом\\sкофе|кофе\\дом|domcof|domkof|dom kof|coffeedom|cofedom|домкофе|кофедом|ljv rjat|\\.ru|\\.ру",
                        false
                }});
    }

    @Test
    public void validateCheckPhrase() {
        assertEquals(
                isValid,
                RegexpValidator.validRegex(checkPhrase)
        );
    }
}
