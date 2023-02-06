package ru.yandex.metrika.expenses.connectors;

import java.util.Map;

import org.junit.Assert;
import org.junit.Test;

import static ru.yandex.metrika.expenses.connectors.AdsConnectorsUtils.decodeWithIllegalArgumentSuppression;

public class AdsConnectorsUtilsTest {

    @Test
    public void decodeTest1() {
        var str = "Adw-%D0%A4%D0%B0%D1%80%D1%82%D1%83%D0%BA.RU%2B-%2B%D0%9F%D0%BE%D0%B8%D1%81%D0%BA%2B-%2B%D0%9C%D0%A1%D0%9A%2B-%2B%D0%A1%D0%BA%D0%B8%D0%BD%D0%B0%D0%BB%D0%B8%2B%D0%A4%D0%B0%D1%80%D1%82%D1%83%D0%BA%2B%D0%9A%D0%BB%D0%B8%D0%BA%D0%B8%2Bv5";
        var result = decodeWithIllegalArgumentSuppression(str);
        Assert.assertEquals("Adw-Фартук.RU+-+Поиск+-+МСК+-+Скинали+Фартук+Клики+v5", result);
    }

    @Test
    public void decodeTest2() {
        var str = "Adw-Фартук.RU+-+Поиск+-+МСК+-+Скинали+Фартук+Клики+v5";
        var result = decodeWithIllegalArgumentSuppression(str);
        Assert.assertEquals("Adw-Фартук.RU - Поиск - МСК - Скинали Фартук Клики v5", result);
    }

    @Test
    public void decodeTest3() {
        var str = "a+b";
        var result = decodeWithIllegalArgumentSuppression(str);
        Assert.assertEquals("a b", result);
    }

    @Test
    public void decodeTestFailed(){
        var str = "%_0";
        var result = decodeWithIllegalArgumentSuppression(str);
        Assert.assertEquals("%_0", result);
    }

    @Test
    public void decodeTest5(){
        var str = "%25";
        var result = decodeWithIllegalArgumentSuppression(str);
        Assert.assertEquals("%", result);
    }

    @Test
    public void extractParamsTest1() {
        var str = "{lpurl}";
        var result = AdsConnectorsUtils.extractParamsFromQueryPart(str);
        Assert.assertEquals(Map.of(), result);
    }

    @Test
    public void extractParamsTest2() {
        var str = "utm_source=eLama-google&" +
                "utm_medium=cpc&" +
                "utm_campaign=Adw-Фартук.RU+-+Поиск+-+МСК+-+Скинали+Фартук+Клики+v5&" +
                "utm_content=cid|{campaignid}|gid|{adgroupid}|aid|{creative}|dvc|{device}|pid|{targetid}|pos|{adposition}|adn|{network}|mt|{matchtype}&" +
                "utm_term={keyword}";
        var result = AdsConnectorsUtils.extractParamsFromQueryPart(str);
        var expected = Map.of("utm_source", "eLama-google",
                "utm_medium", "cpc",
                "utm_campaign", "Adw-Фартук.RU - Поиск - МСК - Скинали Фартук Клики v5",
                "utm_content", "cid|{campaignid}|gid|{adgroupid}|aid|{creative}|dvc|{device}|pid|{targetid}|pos|{adposition}|adn|{network}|mt|{matchtype}",
                "utm_term","{keyword}");
        Assert.assertEquals(expected.size(), result.size());
        for ( var entrySet : result.entrySet()) {
            Assert.assertEquals(expected.get(entrySet.getKey()), entrySet.getValue());
        }
    }

    @Test
    public void extractParamsTest3() {
        var str = "=&=";
        var result = AdsConnectorsUtils.extractParamsFromQueryPart(str);
        Assert.assertEquals(Map.of(), result);
    }

    @Test
    public void extractParamsTest4() {
        var str = "utm_source=some1%25&" +
                "utm_medium=insta_lal1%_4000&" +
                "utm_campaign=inst+lal&" +
                "utm_content=2";
        var result = AdsConnectorsUtils.extractParamsFromQueryPart(str);
        var expected = Map.of("utm_source", "some1%",
                "utm_medium", "insta_lal1%_4000",
                "utm_campaign", "inst lal",
                "utm_content", "2");
        Assert.assertEquals(expected.size(), result.size());
        for ( var entrySet : result.entrySet()) {
            Assert.assertEquals(expected.get(entrySet.getKey()), entrySet.getValue());
        }

    }
}

