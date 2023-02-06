package ru.yandex.autotests.turkey.data;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static org.hamcrest.core.AllOf.allOf;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 03.12.2014.
 */
public class FootballData {
    private static final Properties CONFIG = new Properties();
    public static final String QUESTION_TEXT = "Takımına özel bu temayı varsayılan tema olarak kaydetmek ister misin?";

    public static LinkInfo CANCEL_LINK = new LinkInfo(
            equalTo("Kapat"),
            equalTo(CONFIG.getBaseURL() + "/"),
            hasAttribute(HREF, equalTo(CONFIG.getBaseURL() + "/"))
    );

    public static LinkInfo getAcceptLink(WebDriver driver, FootballClub club) {
        return new LinkInfo(
                equalTo("Kaydet"),
                equalTo(CONFIG.getBaseURL()),
                hasAttribute(HREF,
                        allOf(
                                startsWith(CONFIG.getBaseURL() + "/portal/set/any/"),
//                                containsString("retdom=com.tr"),
                                containsString("sk=" + CookieManager.getSecretKey(driver)),
                                containsString("fttrpr=" + club.getShortName())
                        )
                )
        );
    }

    public static LinkInfo getResetLink(WebDriver driver) {
        return new LinkInfo(
                equalTo("Orjinal temaya dön"),
                equalTo(CONFIG.getBaseURL()),
                hasAttribute(HREF,
                        allOf(
                                startsWith(CONFIG.getBaseURL() + "/portal/set/any/"),
//                                containsString("retdom=com.tr"),
                                containsString("sk=" + CookieManager.getSecretKey(driver))
//                                endsWith("fttrpr=")
                        )
                )
        );
    }

    public enum FootballClub {
//        FENERBAHCE("fb"),
        GALATASARAY("gs"),
        BESIKTAS("bjk");

        private static final String FOOTBALL_URL_PATTERN = CONFIG.getBaseURL() + "/%s";
        private String shortName;

        FootballClub(String shortName) {
            this.shortName = shortName;
        }

        public String getShortName() {
            return this.shortName;
        }

        public static List<FootballClub> getAllClubs() {
            return new ArrayList<>(Arrays.asList(FootballClub.values()));
        }

        public static List<FootballClub> getAllOtherClubs(FootballClub current) {
            List<FootballClub> result = FootballClub.getAllClubs();
            result.remove(current);
            return result;
        }

        public String getFootballClubUrl() {
            return String.format(FOOTBALL_URL_PATTERN, this.getShortName());
        }
    }
}
