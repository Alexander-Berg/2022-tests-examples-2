package ru.yandex.autotests.morda.steps.html;

import org.apache.log4j.Logger;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Node;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/07/16
 */
public class HtmlUtils {
    private static final Logger LOGGER = Logger.getLogger(HtmlUtils.class);
    private static final List<String> BAD_HTML_SUBSTRINGS = asList("undefined", "object Object", "NaN");

    public static String removeScriptTags(String html) {
        LOGGER.info("Removing script tags from html");
        Document doc = Jsoup.parse(html);
        doc.select("script").forEach(Node::remove);
        doc.outputSettings().prettyPrint(false);
        return doc.toString();
    }

    public static Set<String> getAllLinksFromHtml(String html) {
        LOGGER.info("Getting all links from html");
        Set<String> result = new HashSet<>();

        Document doc = Jsoup.parse(html);
        doc.select("script").forEach(Node::remove);
        doc.select("*[href]").forEach(e -> result.add(toUrl(e.attr("href"))));
        doc.select("*[src]").forEach(e -> result.add(toUrl(e.attr("src"))));

        LOGGER.info("Found " + result.size() + " links");

        return result;
    }

    private static String toUrl(String url) {
        if (url == null || !url.startsWith("//")) {
            return url;
        }
        return "https:" + url;
    }

    public static List<String> getSubstrings(String source, String str) {
        List<String> allMatches = new ArrayList<>();
        Matcher m = Pattern.compile("(.{0,50}" + str + ".{0,50})").matcher(source);

        LOGGER.info("Find matches in html: " + m.pattern());

        while (m.find()) {
            allMatches.add(m.group());
        }

        return allMatches;
    }

    public static Map<String, List<String>> getBadHtmlParts(String html) {
        LOGGER.info("Get invalid html parts");
        String normalizedHtml = removeScriptTags(html);

        Map<String, List<String>> result = new HashMap<>();

        BAD_HTML_SUBSTRINGS.stream()
                .forEach(e -> {
                    List<String> matches = getSubstrings(normalizedHtml, e);
                    if (!matches.isEmpty()) {
                        result.put(e, matches);
                    }
                });

        return result;
    }

}
