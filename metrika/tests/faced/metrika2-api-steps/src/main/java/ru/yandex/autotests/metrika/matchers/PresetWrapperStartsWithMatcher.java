package ru.yandex.autotests.metrika.matchers;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;

public class PresetWrapperStartsWithMatcher extends TypeSafeMatcher<PresetWrapper> {

    private String startsWith;

    private PresetWrapperStartsWithMatcher(String startsWith) {
        this.startsWith = startsWith;
    }

    @Override
    protected boolean matchesSafely(PresetWrapper presetWrapper) {
        return presetWrapper != null && presetWrapper.toString().startsWith(startsWith);
    }

    @Override
    public void describeTo(Description description) {
        description.appendText("Пресет начинается с " + startsWith);
    }

    public static Matcher<PresetWrapper> presetStartsWith(String startsWith) {
        return new PresetWrapperStartsWithMatcher(startsWith);
    }
}
