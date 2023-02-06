package ru.yandex.autotests.metrika;

/**
 * Created by okunev on 20.10.2014.
 */
public class Requirements {

    public static final String LONG_RUNNING = "Длительное";

    public final class Feature {
        public static final String MANAGEMENT = "API управления";
        public static final String REPORT = "API отчетов v1";
        public static final String GLOBAL_REPORT = "Глобальный отчет";
        public static final String DATA = "Данные отчетов";
        public static final String LEGACY = "Отчёты предыдущей версии";
        public static final String INPAGE = "In-page аналитика";
        public static final String WEBVISOR = "Отчет по вебвизору";
        public static final String VISITORS = "Грид постетителй";
        public static final String CALLTRACKING = "Целевой звонок";

        public static final String ADVERTISING = "клики Директа";
        public static final String ECOMMERCE = "eCommerce";
        public static final String YAN = "РСЯ";
        public static final String EXPENSES = "Рекламные расходы";
        public static final String USER_CENTRIC = "User centric сегментация";
        public static final String INTERNAL = "Внутренние ручки";
        public static final String ANALYTICS = "API, совместимый с Google Analytics";
        public static final String NDA = "NDA атрибуты и ручки";

        public static final String JSON_SCHEMAS = "Json-схемы";

        public static final String CLIMETR = "Мобильное приложение метрики";

        public static final String HTTPS_ONLY = "https";
    }

    public final class Story {

        public static final String USER_CENTRIC = "User centric сегментация";

        public final class Management {
            public static final String COUNTERS = "Управление счетчиками";
            public static final String LABELS = "Управление метками";
            public static final String SEGMENTS = "Управление сегментами";
            public static final String GRANTS = "Управление доступом";
            public static final String GOALS = "Управление целями";
            public static final String OPERATIONS = "Управлене операциями";
            public static final String QUOTAS = "Информация о квотах";
            public static final String DELEGATE = "Управление представителями";
            public static final String PERMISSION = "Права доступа";
            public static final String NOTIFICATIONS = "Уведомления";
            public static final String CALL_TRACKING = "Целевой звонок";
            public static final String OFFLINE_CONVERSION = "Офлайн конверсии";
            public static final String YCLID_CONVERSION = "Yclid конверсии";
            public static final String CLIENT_SETTINGS = "Пользовательские настройки новостной рассылки";
            public static final String USER_PARAMETERS = "Параметры посетителей";
            public static final String EXPENSE = "Расходы";
            public static final String CHART_ANNOTATIONS = "Примечания на графиках";
            public static final String REPORT_ORDER = "Заказанные отчеты";
            public static final String WEBMASTER_LINK = "Интеграция с Вебмастером";
            public static final String LOGS_API = "Logs API";
            public static final String SUBSCRIPTION = "Подписки пользователя";
            public static final String ADS_CONNECTORS = "Подключения рекламных кабинетов";
            public static final String PARTNERS_GOALS = "Партнёрские цели";
        }

        public final class Report {

            public static final String MANUAL_SAMPLES = "Отобранные в ручную запросы для b2b";
            public static final String PARAMETRIZATION = "Параметризация";
            public static final String ATTRIBUTES_ACCESS = "Доступ к измерениям/метрикам";
            public static final String NAMESPACES = "Пространства имен";
            public static final String SUB_TABLES = "Подтаблицы";
            public static final String TOTALS = "Итоговые значения";
            public static final String ATTRIBUTION = "Атрибуция";
            public static final String AUTHORIZATION = "Авторизация";
            public static final String ADVERTISING = "Клики Директа";
            public static final String DIRECT_CLIENT_IDS_AUTHORIZATION = "Авторизация по direct_client_ids";
            public static final String DIRECT_CLIENT_LOGINS_AUTHORIZATION = "Авторизация по direct_client_logins";
            public static final String RANKED_COUNTERS = "Доступ к блатным счетчикам";
            public static final String PARTNER_MONEY = "Доступ к данным по РСЯ";
            public static final String PERMISSION = "Права доступа";
            public static final String METADATA = "Метаданные";
            public static final String QUERY = "Запрос";
            public static final String CHART_ANNOTATIONS = "Примечания на графиках";
            public static final String REPORT_ORDER = "Заказанные отчеты";

            public final class Type {
                public static final String TABLE = "Таблица";
                public static final String DRILLDOWN = "Drill down";
                public static final String BYTIME = "Получение данных по времени";
                public static final String COMPARISON = "Сравнение сегментов";
                public static final String COMPARISON_DRILLDOWN = "Сравнение - drill down";
                public static final String ECOMMERCE_ORDERS = "Содержимое заказов";
                public static final String ANALYTICS = "Отчет Google Analytics";
                public static final String OFFLINE_CALLS_LOG = "Лог звонков";
                public static final String CROSS_DEVICE = "Кросс-девайс";
                public static final String VISITORS_GRID = "Отчеты по посетителям";
            }

            public final class Format {
                public static final String CSV = "Формат csv";
                public static final String XLSX = "Формат xlsx";
            }

            public final class Parameter {
                public static final String DIMENSIONS = "Параметр dimensions";
                public static final String FILTERS = "Параметр filters";
                public static final String GROUP = "Параметр group";
                public static final String METRICS = "Параметр metrics";
                public static final String PRESET = "Параметр preset";
                public static final String ROW_IDS = "Параметр row_ids";
                public static final String TOP_KEYS = "Параметр top_keys";
                public static final String ACCURACY = "Параметр accuracy";
                public static final String PARENT_ID = "Параметр parent_id";
                public static final String LIMIT = "Параметр limit";
                public static final String OFFSET = "Параметр offset";
                public static final String SORT = "Параметр sort";
                public static final String TIMEZONE = "Параметр timezone";
                public static final String LANG = "Параметр lang";
                public static final String DATE = "Параметры date1 и date2";
                public static final String INCLUDE_UNDEFINED = "Параметр include_undefined";
                public static final String CALLBACK = "Параметр callback";
                public static final String CONFIDENCE = "Режим доверия к данным";
                public static final String DIRECT_CLIENT_IDS = "Параметр direct_client_ids";
                public static final String DIRECT_CLIENT_LOGINS = "Параметр direct_client_logins";
                public static final String IDS = "Параметр ids";
            }

        }

        public final class Inpage {
            public static final String FORM = "Аналитика форм";
            public static final String LINK = "Карта ссылок";
            public static final String CLICK = "Карта кликов";
            public static final String SCROLL = "Карта скроллинга";
            public static final String SEGMENTATION = "Сегментация";
            public static final String MASKS = "Маски урлов";
        }

        public final class WebVisor {
            public static final String VISITS_GRID = "Таблица визитов";
            public static final String HITS_GRID = "Таблица просмотров";
        }

        public final class Visitors {
            public static final String GRID = "Таблица посетителей";
            public static final String INFO = "Информация о посетителе";
            public static final String VISITS = "Список визитов посетителя";
            public static final String COMMENTS = "Комментарий к посетителю";
        }

        public final class Internal {
            public static final String TIME_ZONES = "Список часовых поясов";
            public static final String NOTIFICATIONS = "Уведомления";
            public static final String JSON_SCHEMAS = "Json-схемы";
            public static final String JSON_VALIDATION = "Валидация ответов";
            public static final String CLIENT_SETTINGS = "Пользовательские настройки новостной рассылки";
        }

    }

}
