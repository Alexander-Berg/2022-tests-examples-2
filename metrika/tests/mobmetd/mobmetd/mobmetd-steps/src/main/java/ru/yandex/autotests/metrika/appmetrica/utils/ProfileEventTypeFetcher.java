package ru.yandex.autotests.metrika.appmetrica.utils;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;

import java.util.function.BiFunction;

import static ru.yandex.metrika.segments.apps.bundles.AppEventType.*;

public enum ProfileEventTypeFetcher {
    CLIENT(EVENT_CLIENT) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getClientEventValue(parameters);
        }
    },
    CRASH(EVENT_CRASH) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getCrashEventValue(parameters);
        }
    },
    DEEPLINK(EVENT_OPEN) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getDeeplinkEventValue(parameters);
        }
    },
    ECOM(ECOMMERCE) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getEcomEventValue(parameters);
        }
    },
    REVENUE(EVENT_REVENUE) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getRevenueEventValue(parameters);
        }
    },
    ERROR(EVENT_ERROR) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getErrorEventValue(parameters);
        }
    },
    PROTOBUF_CRASH(EVENT_PROTOBUF_CRASH) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getProtobufCrashEventValue(parameters);
        }
    },
    PROTOBUF_ERROR(EVENT_PROTOBUF_ERROR) {
        @Override
        public BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier() {
            return (userSteps, parameters) -> userSteps.onProfileSteps().getProtobufErrorEventValue(parameters);
        }
    };

    public final AppEventType appEventType;

    ProfileEventTypeFetcher(AppEventType appEventType) {
        this.appEventType = appEventType;
    }

    public abstract BiFunction<UserSteps, IFormParameters, String> getEventValueSupplier();
}
