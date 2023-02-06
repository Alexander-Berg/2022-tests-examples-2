package ru.yandex.autotests.metrika.appmetrica.tests;

/**
 * Created by konkov on 05.07.2016.
 */
public final class Requirements {
    public static final class Feature {

        public static final String AUTH = "Авторизация";

        public static final String DATA = "Данные отчетов";

        public static final class Management {
            public static final String ORGANIZATIONS = "Организация";
            public static final String APPLICATION = "Приложение";
            public static final String PUSH_CAMPAIGN = "Пуш кампания";
            public static final String PUSH_CREDENTIALS = "Учетные данные для рассылки пушей";
            public static final String TRACKER = "Трекер";
            public static final String PARTNERS = "Партнеры";
            public static final String TEST_DEVICES = "Тестовые устройства";
            public static final String SEGMENT = "Работа с сегментами";
            public static final String FUNNELS = "Работа с воронками";
            public static final String PROFILE = "Работа с профилями";
            public static final String CRASH = "Крэши";
            public static final String REVENUE = "Revenue";
            public static final String CLOUD = "Экспорт в облако";
            public static final String SKAD = "SKAdNetwork";

            public static class Partner {
                public static final String POSTBACK_TEMPLATE = "Шаблоны постбеков";
                public static final String ADWORDS = "Партнер Google Adwords";
            }

            public static class Tracker {
                public static final String MANDATORY_POSTBACK = "Обязательный постбек";
            }

            public static final class Application {

                public static final String GRANTS = "Доступ к приложению";

                public static final class Grants {
                    public static final String AGENCY = "Агентский доступ к приложению";
                }

                public static final String EVENTS = "Управление событиями";

            }

            public static final String LIVE_METRICS = "Live метрики";
        }
    }

    public static final class Story {

        public static final String AUTH = "Авторизация";

        public static final String MANUAL_SAMPLES = "Отобранные в ручную запросы для b2b";

        public static final String METRICS = "Метрики";
        public static final String DIMENSIONS = "Группировки";
        public static final String COHORT_ANALYSIS = "Когортный анализ";
        public static final String COHORT_ANALYSIS_V2 = "Когортный анализ v2";
        public static final String TRAFFIC_SOURCES = "Источники трафика";
        public static final String ACTIVITY = "Активность";
        public static final String SAMPLING = "Работа семплирования";
        public static final String QUERY = "Гененерация запросов";

        public static final class Organizations {
            public static final String ADD = "Добавление организации";
            public static final String EDIT = "Редактирование организации";
            public static final String DELETE = "Удаление организации";
            public static final String LIST = "Информация о сохранённых организациях";
            public static final String ADD_TO_ORGANIZATION = "Добавление приложения в организацию";
            public static final String REMOVE_FROM_ORGANIZATION = "Удаление приложения из организации";
            public static final String INFO = "Информация об организации";
        }

        public static final class Application {
            public static final String ADD = "Добавление приложения";
            public static final String EDIT = "Изменение приложения";
            public static final String DELETE = "Удаление приложения";
            public static final String LIST = "Список приложений";
            public static final String INFO = "Информация о приложении";
            public static final String CATEGORIES = "Список категорий приложений";

            public static final class Grants {

                public static final String UNSUBSCRIBE = "Удаление своего гостевого доступа";

                public static final String ADD = "Создание доступа";
                public static final String LIST = "Список прав";
                public static final String INFO = "Информация о доступе конкретного пользователя";
                public static final String QUOTA = "Квоты";

                public static final class Agency {
                    public static final String ADD = "Создание агентского доступа";
                    public static final String EDIT = "Редактирование агентского доступа";
                    public static final String DELETE = "Удаление агентского доступа";
                    public static final String LIST = "Список агентских прав";
                    public static final String INFO = "Информация об агентском доступе конкретного пользователя";
                }
            }

            public static final class EventsManagement {
                public static final String LIST = "Список событий (управление)";
                public static final String EDIT = "Изменение фильтров события";
            }
        }

        public static final class TestDevices {
            public static final String ADD = "Добавление тестового устройства";
            public static final String EDIT = "Редактирование тестового устройства";
            public static final String DELETE = "Удаление тестового устройства";
            public static final String LIST = "Список тестовых устройств";
        }

        public static final class Partner {
            public static final String ADD = "Создание партнера";
            public static final String EDIT = "Редактирование партнера";
            public static final String DELETE = "Удаление партнера";
            public static final String LIST = "Список партнеров";
            public static final String INFO = "Информация о партнере";
            public static final String CSV = "CSV файл с партнерами";

            public static final String TRACKER_COUNT = "Количество трекеров партнера";

            public static final class Adwords {
                public static final String DUPLICATE_CONVERSION = "Проверка ошибочного дублирования параметров " +
                        "Adwords трекера";
            }

            public static final class PostbackTemplate {
                public static final String ADD = "Создание шаблона постбека";
                public static final String EDIT = "Редактирование шаблона постбека";
                public static final String DELETE = "Удаление шаблона постбека";
                public static final String LIST = "Список шаблонов постбеков";
                public static final String INFO = "Информация о шаблоне постбека";
            }
        }

        public static final class Tracker {
            public static final String ADD = "Создание трекера";
            public static final String EDIT = "Редактирование трекера";
            public static final String DELETE = "Удаление трекера";
            public static final String RESTORE = "Восстановление трекера";
            public static final String LIST = "Список трекеров";
            public static final String INFO = "Информация о трекере";
            public static final String CSV = "CSV файл с трекерами";

            public static final class Postback {

                public static final class MandatoryPostback {
                    public static final String ADD = "Создание обязательного постбека";
                    public static final String EDIT = "Редактирование обязательного постбека";
                    public static final String DELETE = "Удаление обязательного постбека";
                }

            }
        }

        public static final class Profile {
            public static final class Attributes {
                public static final String ADD = "Добавление атрибута профиля";
                public static final String DELETE = "Удаление атрибута профиля";
                public static final String RESTORE = "Восстановление атрибута профиля";
                public static final String LIST = "Получение списка атрибутов профиля";
            }

            public static final class Events {
                public static final String NAMES = "Загрузка имён событий профиля";
                public static final String SESSIONS = "Загрузка цепочек событий профиля";
                public static final String UNWRAP = "Разворачивание события профиля";
                public static final String VALUE = "Получение значения события профиля";
            }
        }

        public static final class PushCampaign {
            public static final String ADD = "Создание пуш кампании";
            public static final String LIST = "Список пуш кампаний";
            public static final String LAUNCH = "Запуск пуш кампаний";
            public static final String ESTIMATION = "Оценка аудитории пуш кампании";
        }

        public static final class PushCredentials {
            public static final String ADD = "Добавление данных учетной записи";
            public static final String DELETE = "Удаление данных учетной записи";
            public static final String LIST = "Информация об учетных данных";
        }

        public static final class Segments {
            public static final String ADD = "Добавление сегмента";
            public static final String EDIT = "Редактирование сегмента";
            public static final String DELETE = "Удаление сегмента";
            public static final String LIST = "Информация о сохранённых сегментах";
            public static final String CONVERT = "Конвертация сегмента в формат апи";
        }

        public static final class Funnels {
            public static final String ADD = "Добавление воронки";
            public static final String EDIT = "Редактирование воронки";
            public static final String DELETE = "Удаление воронки";
            public static final String LIST = "Информация о сохранённых воронках";
        }

        public static final class LiveMetrics {
            public static final String EXISTS = "Получение live метрик";
        }

        public static final class Type {
            public static final String TABLE = "Таблица";
            public static final String DRILLDOWN = "Drill down";
            public static final String BYTIME = "Получение данных по времени";
            public static final String TREE = "Дерево";
        }

        public static final class Crash {
            public static final class CrashGroup {
                public static final String COMMENT = "Редактирование комментария крэш-группы";
                public static final String STATUS = "Редактирование статуса крэш-группы";
            }

            public static final String PROGUARD_MAPPING_UPLOAD = "Загрузка proguard mapping.txt";
            public static final String ANDROID_NATIVE_SYMBOLS_UPLOAD = "Загрузка android native символов";
            public static final String DSYM_UPLOAD = "Загрузка dSYM";

            public static final String ANDROID_SYMBOLS_LIST = "Список загруженных и недостающих символов Android";
            public static final String ANDROID_SYMBOLS_MISSING_STAT = "Статистика о недостающих символах Android";
            public static final String DSYM_LIST = "Список dSYM";
            public static final String DSYM_MISSING_STAT = "Статистика о недостающих dSYM";

            public static final String STACKTRACE = "Получение списка стектрейсов креша";

            public static final String ALERT_SETTINGS = "Редактирование настроек оповещений";
        }

        public static final class Revenue {
            public static final String LIST_REVENUE_CURRENCIES = "Валюты revenue-отчёта";
        }

        public static final class RevenueCredentials {
            public static final String EDIT = "Редактирование данных о валидации покупок";
        }

        public static final class RevenueSettings {
            public static final String EDIT = "Редактирование настроек отчётов и постбеков по revenue";
        }

        public static final class CloudAuthKeys {
            public static final String EDIT = "Редактирование данных о ключах для экспорта в облако";
        }

        public static final class CloudExports {
            public static final String MANAGEMENT = "Управление экспортом в облако";
            public static final String VALIDATION = "Валидация экспорта в облако";
            public static final String GET_META = "Получение меты для экспорта в облако";
        }

        public static final class CloudClusters {
            public static final String GET_LIST = "Получение списка кластеров";
        }

        public static final class SKAdConversionValue {
            public static final String INFO = "Информация о SKAd Conversion Value конфигурации";
            public static final String EDIT = "Редактирование SKAd Conversion Value конфигурации";
        }

        public static final class SKAdReport {
            public static final String REPORT_ACCESS = "Доступ к SKAd-отчёту";
        }
    }
}
