package ru.yandex.autotests.metrika.appmetrica.utils;

import org.apache.http.NameValuePair;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.metrika.spring.profile.ProfileData;

import static ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers.similarTo;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ProfileB2BMatchers.similarProfiles;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ProfileB2BMatchers.similarProfilesReport;

/**
 * Created by konkov on 06.07.2016.
 */
public final class ReportTypes {

    public static final ReportType<StatV1DataGETSchema> TABLE = new ReportType<StatV1DataGETSchema>() {
        @Override
        public String getTitle() {
            return "table";
        }
        @Override
        public StatV1DataGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onReportSteps().getTableReport(parameters);
        }
        @Override
        public ProfileData getProfileData(StatV1DataGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(StatV1DataGETSchema testingBean, StatV1DataGETSchema referenceBean) {
            UserSteps.assumeOnResponses(testingBean, referenceBean);
        }
        @Override
        public Matcher<StatV1DataGETSchema> getB2bMatcher(StatV1DataGETSchema referenceBean) {
            return similarTo(referenceBean);
        }
    };

    public static final ReportType<StatV1DataDrilldownGETSchema> DRILLDOWN = new ReportType<StatV1DataDrilldownGETSchema>() {
        @Override
        public String getTitle() {
            return "drill down";
        }
        @Override
        public StatV1DataDrilldownGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onReportSteps().getDrillDownReport(parameters);
        }
        @Override
        public ProfileData getProfileData(StatV1DataDrilldownGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(StatV1DataDrilldownGETSchema testingBean, StatV1DataDrilldownGETSchema referenceBean) {
            UserSteps.assumeOnResponses(testingBean, referenceBean);
        }
        @Override
        public Matcher<StatV1DataDrilldownGETSchema> getB2bMatcher(StatV1DataDrilldownGETSchema referenceBean) {
            return similarTo(referenceBean);
        }
    };

    public static final ReportType<StatV1DataBytimeGETSchema> BYTIME = new ReportType<StatV1DataBytimeGETSchema>() {
        @Override
        public String getTitle() {
            return "bytime";
        }
        @Override
        public StatV1DataBytimeGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onReportSteps().getByTimeReport(parameters);
        }
        @Override
        public ProfileData getProfileData(StatV1DataBytimeGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(StatV1DataBytimeGETSchema testingBean, StatV1DataBytimeGETSchema referenceBean) {
            UserSteps.assumeOnResponses(testingBean, referenceBean);
        }
        @Override
        public Matcher<StatV1DataBytimeGETSchema> getB2bMatcher(StatV1DataBytimeGETSchema referenceBean) {
            return similarTo(referenceBean);
        }
    };

    public static final ReportType<StatV1SegmentTreeGETSchema> TREE = new ReportType<StatV1SegmentTreeGETSchema>() {
        @Override
        public String getTitle() {
            return "tree";
        }
        @Override
        public StatV1SegmentTreeGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onReportSteps().getTree(parameters);
        }
        @Override
        public ProfileData getProfileData(StatV1SegmentTreeGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(StatV1SegmentTreeGETSchema testingBean, StatV1SegmentTreeGETSchema referenceBean) {
            UserSteps.assumeOnResponses(testingBean, referenceBean);
        }
        @Override
        public Matcher<StatV1SegmentTreeGETSchema> getB2bMatcher(StatV1SegmentTreeGETSchema referenceBean) {
            return similarTo(referenceBean);
        }
    };

    public static final ReportType<V1CohortAnalysisGETSchema> COHORT = new ReportType<V1CohortAnalysisGETSchema>() {
        @Override
        public String getTitle() {
            return "cohort";
        }
        @Override
        public V1CohortAnalysisGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onCohortAnalysisSteps().getReport(parameters);
        }
        @Override
        public ProfileData getProfileData(V1CohortAnalysisGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(V1CohortAnalysisGETSchema testingBean, V1CohortAnalysisGETSchema referenceBean) {
            UserSteps.assumeOnCaResponses(testingBean.getCohortAnalysisData(), referenceBean.getCohortAnalysisData());
        }
        @Override
        public Matcher<V1CohortAnalysisGETSchema> getB2bMatcher(V1CohortAnalysisGETSchema referenceBean) {
            return similarTo(referenceBean);
        }
    };

    public static final ReportType<V2UserAcquisitionGETSchema> USER_ACQUISITION = new ReportType<V2UserAcquisitionGETSchema>() {
        @Override
        public String getTitle() {
            return "user acquisition";
        }
        @Override
        public V2UserAcquisitionGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onTrafficSourceSteps().getReport(parameters);
        }
        @Override
        public ProfileData getProfileData(V2UserAcquisitionGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(V2UserAcquisitionGETSchema testingBean, V2UserAcquisitionGETSchema referenceBean) {
            UserSteps.assumeOnResponses(testingBean, referenceBean);
        }
        @Override
        public Matcher<V2UserAcquisitionGETSchema> getB2bMatcher(V2UserAcquisitionGETSchema referenceBean) {
            return similarTo(referenceBean);
        }
    };

    public static final ReportType<StatV1ProfilesGETSchema> PROFILE_REPORT = new ReportType<StatV1ProfilesGETSchema>() {
        @Override
        public String getTitle() {
            return "profile report";
        }
        @Override
        public StatV1ProfilesGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onProfileSteps().getReport(parameters);
        }
        @Override
        public ProfileData getProfileData(StatV1ProfilesGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(StatV1ProfilesGETSchema testingBean, StatV1ProfilesGETSchema referenceBean) {
            UserSteps.assumeOnResponses(testingBean, referenceBean);
        }
        @Override
        public Matcher<StatV1ProfilesGETSchema> getB2bMatcher(StatV1ProfilesGETSchema referenceBean) {
            return similarProfilesReport(referenceBean);
        }
    };

    public static final ReportType<StatV1DataGETSchema> PROFILE_LIST = new ReportType<StatV1DataGETSchema>() {
        @Override
        public String getTitle() {
            return "profile list";
        }
        @Override
        public StatV1DataGETSchema getReport(UserSteps steps, IFormParameters parameters) {
            return steps.onProfileSteps().getListReport(parameters);
        }
        @Override
        public ProfileData getProfileData(StatV1DataGETSchema bean) {
            return bean.getProfile();
        }
        @Override
        public void assumeOnResponses(StatV1DataGETSchema testingBean, StatV1DataGETSchema referenceBean) {
            UserSteps.assumeOnResponses(testingBean, referenceBean);
        }
        @Override
        public Matcher<StatV1DataGETSchema> getB2bMatcher(StatV1DataGETSchema referenceBean) {
            return similarProfiles(referenceBean);
        }
    };

    public static Long extractAppId(IFormParameters parameters) {
        for (NameValuePair pair : parameters.getParameters()) {
            if ("id".equals(pair.getName()) || "appId".equals(pair.getName())) {
                return Long.parseLong(pair.getValue());
            }
        }
        throw new IllegalArgumentException("Application id not found. " + parameters);
    }
}
