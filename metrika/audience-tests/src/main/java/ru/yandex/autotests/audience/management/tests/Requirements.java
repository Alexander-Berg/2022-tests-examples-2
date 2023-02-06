package ru.yandex.autotests.audience.management.tests;

/**
 * Created by konkov on 23.03.2017.
 */
public final class Requirements {

    public final class Feature {
        public static final String MANAGEMENT = "API Управления";
        public static final String AudienceCryptaSender = "API создания сегментов";
    }

    public final class Story {
        public final class Management {
            public static final String SEGMENTS = "Управление сегментами";
            public static final String GRANTS = "Управление доступом";
            public static final String ACCOUNTS = "Управление аккаунтами";
            public static final String DELEGATES = "Управление представителями";
            public static final String PIXELS = "Управление пикселями";
            public static final String EXPERIMENTS = "Управление экспериментами";

            public final class Segment {
                public static final String UPLOADING = "Сегмент из файла";
                public static final String CLIENTID_UPLOADING = "Сегмент из файла по ClientId Метрики";
                public static final String CRM_UPLOADING = "Сегмент из файла CRM-сегмент";
                public static final String PIXEL = "Сегмент с типом «pixel»";
                public static final String LAL = "Сегмент с типом «lookalike»";
                public static final String METRIKA = "Сегмент из объекта метрики";
                public static final String APPMETRICA = "Сегмент из объекта AppMetrica";
                public static final String GEO = "Сегмент с типом «геолокация»";
                public static final String DMP = "Сегмент с типом «dmp»";
                public static final String INTERNAL_DMP = "Сегмент на основе «yuid»";
            }
        }
    }

    public final class StoryCryptaSender {
        public final class AudienceCryptaSender {
            public static final String SEGMENTS = "Управление сегментами";

            public final class Segment {
                public static final String UPLOADING = "Сегмент из файла";
                public static final String CLIENTID_UPLOADING = "Сегмент из файла по ClientId Метрики";
                public static final String CRM_UPLOADING = "Сегмент из файла CRM-сегмент";
                public static final String PIXEL = "Сегмент с типом «pixel»";
                public static final String LAL = "Сегмент с типом «lookalike»";
                public static final String METRIKA = "Сегмент из объекта метрики";
                public static final String APPMETRICA = "Сегмент из объекта AppMetrica";
                public static final String GEO = "Сегмент с типом «геолокация»";
                public static final String DMP = "Сегмент с типом «dmp»";
                public static final String INTERNAL_DMP = "Сегмент на основе «yuid»";
            }
        }
    }
}
