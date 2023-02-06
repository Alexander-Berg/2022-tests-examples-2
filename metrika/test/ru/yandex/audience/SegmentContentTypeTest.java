package ru.yandex.audience;

import java.util.regex.Pattern;

import org.junit.Ignore;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * Created by vesel4ak-u on 05.05.16.
 */
public class SegmentContentTypeTest {

    @Test
    @Ignore("METRIQA-936")
    public void testEmailPattern() {
        String regex = ContentPattern.unescape(ContentPattern.EMAIL); // слеши были удвоены для Clickhouse
        Pattern pattern = Pattern.compile(regex);
        assertEquals(true, pattern.matcher("v@g.ru").matches());
        assertEquals(true, pattern.matcher("._-1.v..g..@g.g.ru").matches());
        assertEquals(false, pattern.matcher("@g.ru").matches());
        assertEquals(false, pattern.matcher("v@g.ru.").matches());
        assertEquals(false, pattern.matcher("V@G.RU").matches());
        assertEquals(false, pattern.matcher("v@.g.ru").matches());
        assertEquals(false, pattern.matcher("v@g..ru").matches());
    }

    @Test
    public void testIdfaGaidPattern() {
        String regex = ContentPattern.unescape(ContentPattern.IDFA_GAID); // слеши были удвоены для Clickhouse
        Pattern pattern = Pattern.compile(regex);
        assertEquals(true, pattern.matcher("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee").matches());
        assertEquals(true, pattern.matcher("AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE").matches());
        assertEquals(false, pattern.matcher("AAAaAAAA-BBbB-CcCC-DDdD-EeEEEEEEEEEE").matches());
    }

    @Test
    public void testMacPattern() {
        String regex = ContentPattern.unescape(ContentPattern.MAC); // слеши были удвоены для Clickhouse
        Pattern pattern = Pattern.compile(regex);
        assertEquals(true, pattern.matcher("5c260a6eb5bf").matches());
        assertEquals(false, pattern.matcher("8675309").matches());
    }

    @Test
    public void testCryptaIdPattern() {
        String regex = ContentPattern.unescape(ContentPattern.CRYPTA_ID); // слеши были удвоены для Clickhouse
        Pattern pattern = Pattern.compile(regex);
        assertEquals(false, pattern.matcher("5c260a6eb5bf").matches());
        assertEquals(true, pattern.matcher("1610859061390061246").matches());
    }

    @Test
    public void testPUIDPattern() {
        String regex = ContentPattern.unescape(ContentPattern.PUID); // слеши были удвоены для Clickhouse
        Pattern pattern = Pattern.compile(regex);
        assertEquals(false, pattern.matcher("5c260a6eb5bf").matches());
        assertEquals(true, pattern.matcher("8675309").matches());

    }

    public static void main(String[] args) {
        String regex = ContentPattern.unescape(ContentPattern.EMAIL); // слеши были удвоены для Clickhouse
        Pattern pattern = Pattern.compile(regex);

        for (String s : new String[]{"kkrikunenko87@mail.ru", "89055776609@MAIL.ru", "VIK-det@mail.ru", "hitrovat@mail.RU", "PNU@mail.ru", "borzoi215@mail.ru",
        "proglot088@gmail.com",
        "sir0529@mail.ru",
        "WWW.nice.dulaev.s@mail.ru",
        "EVGEN5060@gmail.com"}) {
            System.out.println(pattern.matcher(s).matches());
        }
    }
}
