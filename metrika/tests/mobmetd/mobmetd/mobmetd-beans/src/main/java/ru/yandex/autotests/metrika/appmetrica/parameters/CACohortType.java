package ru.yandex.autotests.metrika.appmetrica.parameters;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Тип когорты в КА
 * <p>
 * Created by graev on 03/02/2017.
 */
public class CACohortType {

    private final Type type;

    private final String urlParam;

    public static CACohortType installationDate() {
        return new CACohortType(Type.INSTALLATION_DATE);
    }

    public static CACohortType tracker() {
        return new CACohortType(Type.TRACKER);
    }

    public static CACohortType partner() {
        return new CACohortType(Type.PARTNER);
    }

    public static CACohortType trackerParam(String param) {
        return new CACohortType(Type.TRACKER_PARAM, param);
    }

    public static List<CACohortType> apiDimensions() {
        return Arrays.stream(Type.values())
                .filter(Type::isApiDimension)
                .map(CACohortType::new)
                .collect(Collectors.toList());
    }

    public static CACohortType someApiDimension() {
        return new CACohortType(Type.APP_VERSION);
    }

    private CACohortType(Type type) {
        this(type, null);
    }

    private CACohortType(Type type, String urlParam) {
        this.type = type;
        this.urlParam = urlParam;
    }

    public String getUrlParam() {
        return urlParam;
    }

    public String getApiName() {
        return type.getApiName();
    }

    @Override
    public String toString() {
        if (type == Type.TRACKER_PARAM) {
            return "tracker_param(" + urlParam + ')';
        }
        return type.getApiName();
    }

    private enum Type {
        INSTALLATION_DATE(false, "installation_date"),
        TRACKER(false, "tracker"),
        PARTNER(false, "partner"),
        TRACKER_PARAM(false, "tracker_param"),
        DATE("date"),
        MONTH("month"),
        YEAR("year"),
        DAY_OF_WEEK("day_of_week"),
        DAY_OF_MONTH("day_of_month"),
        START_OF_WEEK("start_of_week"),
        START_OF_MONTH("start_of_month"),
        START_OF_QUARTER("start_of_quarter"),
        STAR_OF_YEAR("start_of_year"),
        INSTALL_SOURCE_TYPE("install_source_type"),
        REGION_CONTINENT("region_continent"),
        REGION_COUNTRY("region_country"),
        REGION_AREA("region_area"),
        REGION_DISTRICT("region_district"),
        REGION_CITY("region_city"),
        REGION_CITY_SIZE("region_city_size"),
        OPERATING_SYSTEM_INFO("operating_system_info"),
        OS_MAJOR_VERSION_INFO("os_major_version_info"),
        OPERATING_SYSTEM_VERSION_INFO("operating_system_version_info"),
        OPERATING_SYSTEM_MINOR_VERSION_INFO("operating_system_minor_version_info"),
        LOCATION_DISABLED("location_disabled"),
        GENDER("gender"),
        AGE_INTERVAL("age_interval"),
        BUILD_NUMBER("build_number"),
        APP_VERSION("app_version"),
        APP_VERSION_DETAILS("app_version_details");

        private final boolean apiDimension;
        private final String apiName;

        Type(String apiName) {
            this(true, apiName);
        }

        Type(boolean customCohortType, String apiName) {
            this.apiDimension = customCohortType;
            this.apiName = apiName;
        }

        public boolean isApiDimension() {
            return apiDimension;
        }

        public String getApiName() {
            return apiName;
        }
    }
}
