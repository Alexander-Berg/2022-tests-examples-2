package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.utils.morda.language.Language;

import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.util.regex.Pattern.compile;

/**
 * User: eoff
 * Date: 05.03.13
 */
public class LanguageMatcher extends TypeSafeMatcher<String> {
    private Language language;

    private static final HashMap<Language, Pattern> PATTERNS = new HashMap<Language, Pattern>() {{
        put(Language.RU,
                compile("[©ёЁа-яА-Яa-zA-Z\\p{Digit}\\p{Space}…№«»\\s—-—–“”„−·↑↓°€$#_!?.,;:%\"'-’\\(\\)/`]*"));
        put(Language.UK,
                compile("[©ҐґЄєІіЇїёЁ’а-яА-Яa-zA-Z\\p{Digit}\\p{Space}…№«»\\s\\-—–“”„−·↑↓°€#_$!?.,;:%\"'-\\(\\)/`]*"));
        put(Language.KK,
                compile("[©ѕЅљЉћЋәӘөӨұҰіІқҚѓЃғҒңҢһҺүҮёЁџЏќЌа-яА-Яa-zA-Z\\p{Digit}\\p{Space}…№«»\\s\\-—–“”„−·" +
                        "↑↓°€#_$!?.,;:%\"'-’\\(\\)/`]*"));
        put(Language.BE,
                compile("[©’ІіЎўёЁа-яА-Яa-zA-Z\\p{Digit}\\p{Space}…№«»\\s\\-—–“”„−·↑↓°!?€#_$.,;:%\"'-\\(\\)/`]*"));
        put(Language.TT,
                compile("[©ѕЅљЉћЋәӘөӨұҰіІқҚѓЃғҒңҢһҺүҮёЁџЏќЌҗа-яА-Яa-zA-Z\\p{Digit}\\p" +
                        "{Space}…№«»\\s\\-—–“”„−·↑↓°€#_$!?.,;:%\"'-’\\(\\)/`]*"));
        put(Language.TR,
                compile("[â©AaBbCcÇçDdEeFfGgĞğHhIıİiJjKkLlMmNnOoÖöPpRrSsŞşTtUuÜüVvYyZzÎîa-zA-Z\\p{Digit}" +
                        "\\p{Space}…№«»\\s\\-—–‘’“”„−·↑↓°€$!?.,;:%\"'-|\\(\\)/`]*"));
    }};


    public LanguageMatcher(Language language) {
        this.language = language;
    }

    @Override
    protected boolean matchesSafely(String s) {
        Matcher matcher = PATTERNS.get(language).matcher(s);
        return matcher.matches();
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("Текст элемента на языке " + language);
    }

    @Override
    protected void describeMismatchSafely(String item, Description mismatchDescription) {
        String text = item;
        String badSymbols = "";
        for (int i = 0; i != text.length(); i++) {
            Matcher matcher = PATTERNS.get(language).matcher(text.substring(i, i + 1));
            if (!matcher.matches()) {
                badSymbols += text.substring(i, i + 1);
            }
        }
        mismatchDescription.appendText("Строка " + text + " содержит неверные символы для языка "
                + language + ": " + badSymbols);
    }

    @Factory
    public static org.hamcrest.Matcher<String> inLanguage(Language language) {
        return new LanguageMatcher(language);
    }
}
