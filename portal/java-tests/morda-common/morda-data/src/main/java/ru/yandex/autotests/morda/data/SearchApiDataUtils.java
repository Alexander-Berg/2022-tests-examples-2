package ru.yandex.autotests.morda.data;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import java.util.stream.Stream;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class SearchApiDataUtils {

    private static final Random RANDOM = new Random();

    public static String getYellowskinkUrl(String url) {
        if (url == null || !url.startsWith("yellowskin://")) {
//            throw new IllegalArgumentException("Not a yellowskin url: " + url);
            return url;
        }

        String urlStart = "url=";

        Optional<String> encodedUrl = Stream.of(url.substring(url.indexOf("?") + 1).split("&"))
                .filter(e -> e.startsWith(urlStart))
                .map(e -> e.substring(urlStart.length()))
                .findFirst();

        if (!encodedUrl.isPresent()) {
            throw new IllegalStateException("Failed to parse yellowskin url: " + url);
        }

        String encoded = encodedUrl.get();
        try {
            return URLDecoder.decode(encoded, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException("Failed to decode url: " + encodedUrl, e);
        }
    }

    public static String getFallbackUrl(String url) {
        if (url == null || !url.startsWith("intent://")) {
            return url;
        }
        String fallbackStart = "S.browser_fallback_url=";

        Optional<String> fallback = Stream.of(url.split(";"))
                .filter(e -> e.startsWith(fallbackStart))
                .map(e -> e.substring(fallbackStart.length()))
                .findFirst();

        if (!fallback.isPresent()) {
            throw new IllegalStateException("Failed to parse intent url: " + url);
        }

        String encodedUrl = fallback.get();
        try {
            return URLDecoder.decode(encodedUrl, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException("Failed to decode url: " + encodedUrl, e);
        }
    }

    public static <T> T getRandomElement(List<T> elements) {
        return elements.get(RANDOM.nextInt(elements.size()));
    }
}
