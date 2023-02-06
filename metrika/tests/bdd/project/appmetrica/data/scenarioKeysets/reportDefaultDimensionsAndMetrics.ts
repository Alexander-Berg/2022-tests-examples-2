export const defaultMetrics : Record<string, string> = {
    UAMetricsRu: "Клики; Установки; Deeplinks; Конверсия; Сессии",
    remarketingMetricsRu: "Клики; Re‑engagements; Deeplinks; Конверсия; Сессии",
    SKADMetricsRu: "Все установки; Новые установки; Повторные установки; Конверсии",
    revenueMetricsRu: "Платящие пользователи; Покупки; Покупок на пользователя;" +
        " Выручка; ARPU; ARPPU; % от всех пользователей",
    ecommerceMetricsRu: "Доход; Покупки; Средний доход на покупку (AOV); " +
        "Пользователи, купившие товар; Покупок на пользователя;" +
        " Средний доход на пользователя (ARPU); Средний доход на платящего пользователя (ARPPU)",
    engagementMetricsRu: "Timespent на пользователя; Сессии; Сессий на пользователя",
    eventsMetricsRu: "Количество событий; Пользователи; Событий на пользователя; % от всех пользователей",
    pushCampaignsMetricsRu:"Отправлено; Доставлено; Открыто; Конверсия"
};

export const defaultDimensions: Record<string, string> = {
    UADimensionsRu: "Партнёры; Трекеры",
    remarketingDimensionsRu: "Партнёры; Трекеры",
    SKADDimensionsRu: "Партнёр; ID кампании",
    revenueDimensionsRu: "День",
    ecommerceDimensionsRu: "День",
    engagementDimensionsRu: "День",
    eventsDimensionsRu: "Событие; Все параметры, ур. 1; Все параметры, ур. 2; " +
            "Все параметры, ур. 3; Все параметры, ур. 4; Все параметры, ур. 5",
    pushCampaignsDimensionsRu:"Push-кампания; Гипотеза; Операционная система; Язык"
};
