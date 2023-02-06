package ru.yandex.autotests.metrika.appmetrica.utils;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.metrika.spring.profile.ProfileData;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by konkov on 06.07.2016.
 */
public abstract class ReportType<ResponseClass> {

    public abstract String getTitle();

    public abstract ResponseClass getReport(UserSteps steps, IFormParameters parameters);

    public abstract ProfileData getProfileData(ResponseClass bean);

    public abstract void assumeOnResponses(ResponseClass testingBean, ResponseClass referenceBean);

    public abstract Matcher<ResponseClass> getB2bMatcher(ResponseClass referenceBean);

    public void assertB2b(UserSteps onTesting, UserSteps onReference, IFormParameters parameters) {
        ResponseClass reference = getReport(onReference, parameters);
        ResponseClass testing = getReport(onTesting, parameters);
        assumeOnResponses(testing, reference);
        assertThat("ответы совпадают", testing, getB2bMatcher(reference));
    }

    @Override
    public String toString() {
        return getTitle();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;

        if (o == null || getClass() != o.getClass()) return false;

        ReportType<?> that = (ReportType<?>) o;

        return new EqualsBuilder()
                .append(getTitle(), that.getTitle())
                .isEquals();
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder(17, 37)
                .append(getTitle())
                .toHashCode();
    }
}
