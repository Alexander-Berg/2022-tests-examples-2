package ru.yandex.metrika.cdp.api.validation.util;

import java.util.Optional;

import org.apache.commons.lang3.builder.ReflectionToStringBuilder;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.hamcrest.TypeSafeMatcher;
import org.hamcrest.core.IsAnything;

import ru.yandex.metrika.api.error.ApiError;
import ru.yandex.metrika.api.error.ValidationException;
import ru.yandex.metrika.util.ApiInputValidator;

public class ValidationMatchers {

    private final ApiInputValidator apiInputValidator;
    private final Class<?>[] groups;

    public ValidationMatchers(ApiInputValidator apiInputValidator, Class<?>... groups) {
        this.apiInputValidator = apiInputValidator;
        this.groups = groups;
    }

    public <T> Matcher<T> valid() {
        return new ValidMatcher<>();
    }

    public <T> Matcher<T> notValid() {
        return new NotValidMatcher<>(new IsAnything<>());
    }

    public <T> Matcher<T> notValidAndErrors(Matcher<Iterable<? super ApiError>> errorMatcher) {
        return new NotValidMatcher<>(errorMatcher);
    }


    public static Matcher<ApiError> withErrorLocation(String location) {
        return new ApiErrorLocationMatcher(Matchers.equalTo(location));
    }

    public static Matcher<ApiError> withErrorLocationStartingWith(String locationPrefix) {
        return new ApiErrorLocationMatcher(Matchers.startsWith(locationPrefix));
    }

    private <T> Optional<ValidationException> doValidation(T item) {
        try {
            apiInputValidator.validate(item, groups);
        } catch (ValidationException e) {
            return Optional.of(e);
        }
        return Optional.empty();
    }

    private class ValidMatcher<T> extends TypeSafeMatcher<T> {
        @Override
        protected boolean matchesSafely(T item) {
            return doValidation(item).isEmpty();
        }

        @Override
        public void describeTo(Description description) {
            description.appendText("valid item");
        }

        @Override
        protected void describeMismatchSafely(T item, Description mismatchDescription) {
            var validationException = doValidation(item).orElseThrow();
            mismatchDescription.appendText("was not valid item ")
                    .appendValue(ReflectionToStringBuilder.toString(item))
                    .appendText(" with errors ")
                    .appendValue(validationException.getErrors());
        }
    }

    private class NotValidMatcher<T> extends TypeSafeMatcher<T> {

        private final Matcher<Iterable<? super ApiError>> errorMatcher;

        private NotValidMatcher(Matcher<Iterable<? super ApiError>> errorMatcher) {
            this.errorMatcher = errorMatcher;
        }

        @Override
        protected boolean matchesSafely(T item) {
            var validationExceptionO = doValidation(item);
            if (validationExceptionO.isEmpty()) {
                return false;
            }
            return errorMatcher.matches(validationExceptionO.get().getErrors());
        }

        @Override
        public void describeTo(Description description) {
            description.appendText("not valid item with errors ").appendDescriptionOf(errorMatcher);
        }

        @Override
        protected void describeMismatchSafely(T item, Description mismatchDescription) {
            var validationExceptionO = doValidation(item);
            if (validationExceptionO.isEmpty()) {
                mismatchDescription.appendText("was valid item ").appendValue(ReflectionToStringBuilder.toString(item));
                return;
            }
            var errors = validationExceptionO.get().getErrors();
            mismatchDescription.appendValue("was not valid item ")
                    .appendValue(ReflectionToStringBuilder.toString(item))
                    .appendText(" with errors ")
                    .appendValue(errors);
        }
    }

    private static class ApiErrorLocationMatcher extends TypeSafeMatcher<ApiError> {

        private final Matcher<String> locationMatcher;

        private ApiErrorLocationMatcher(Matcher<String> locationMatcher) {
            this.locationMatcher = locationMatcher;
        }

        @Override
        protected boolean matchesSafely(ApiError item) {
            return locationMatcher.matches(item.getLocation());
        }

        @Override
        public void describeTo(Description description) {
            description.appendText("ApiError with location ").appendDescriptionOf(locationMatcher);
        }
    }
}
