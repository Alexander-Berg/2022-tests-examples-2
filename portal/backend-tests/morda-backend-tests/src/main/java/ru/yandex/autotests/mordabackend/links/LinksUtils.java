package ru.yandex.autotests.mordabackend.links;

import org.apache.commons.lang3.StringUtils;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Pattern;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class LinksUtils {
    public static final List<String> ALLOWED_HOSTS = Arrays.asList(
            "yandex.ru",
            "yandex.kz",
            "yandex.ua",
            "yandex.by",
            "yandex.com",
            "yandex.com.tr",
            "yandex.net",
            "yandex.st",
            "yastatic.net",
            "ya.ru",
            "rs.mail.ru",
            "yandexgaby.hit.gemius.pl",
            "yandexgaua.hit.gemius.pl",
            "auto.ru",
            "webasr.yandex.net",
            "tts.voicetech.yandex.net",
            "abc.yastatic.net",
            "system.admify.ru",
            "plus.kinopoisk.ru",
            "www.youtube.com",
            "stream.1tv.ru",
            "my.ntv.ru",
            "www.tvc.ru",
            "player.vgtrk.com",
            "moscow.mchs.ru"
    );

    public static final List<String> ALLOWED_TOUCH_HOSTS = Arrays.asList(
            "ad.apps.fm",
            "app.adjust.io",
            "app.adjust.com",
            "app.appsflyer.com",
            "www.windowsphone.com",
            "api-05.com",
            "rs.mail.ru",
            "auto.ru",
            "194039.measurementapi.com",
            "itunes.apple.com"
    );

    public static Pattern getLinksPattern(UserAgent userAgent) {
        List<String> hosts = new ArrayList<>();
        for (String host : ALLOWED_HOSTS) {
            hosts.add(host.replaceAll("\\.", "\\."));
        }
        if (userAgent.getIsTouch() == 1) {
            for (String host : ALLOWED_TOUCH_HOSTS) {
                hosts.add(host.replaceAll("\\.", "\\."));
            }
        }

        String hostsPattren = StringUtils.join(hosts, '|');

        return Pattern.compile("(\\w+:)?\\/\\/(?![^\\/\"]*(\"|" + hostsPattren + "))[^\"]*");
    }
}
