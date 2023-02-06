package ru.yandex.autotests.mordacommonsteps.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.allOf;

/**
 * User: eoff
 * Date: 22.11.12
 */
public class LinkInfo {
    public Matcher<String> text;
    public Matcher<String> url;
    public Matcher<HtmlElement> attributes;

    public LinkInfo(Matcher<String> text, Matcher<String> url) {
        this.text = text;
        this.url = url;
        attributes = HtmlAttributeMatcher.hasAttribute(HtmlAttribute.HREF, url);
    }

    public LinkInfo(Matcher<String> text, Matcher<String> url, HtmlAttributeMatcher... matcher) {
        this.text = text;
        this.url = url;
        attributes = allOf(matcher);
    }

    @Override
    public String toString() {
        return text.toString();
    }
}
