export interface TestConfigBase {
    /**
     * Название теста
     */
    name: string;

    /**
     * высота скриншота
     */
    height?: number;

    /**
     * ширина скриншота
     */
    width?: number;

    /**
     * Пока не поддержана. https://st.yandex-team.ru/MOBSEARCHANDROID-35270
     * Планируется уметь дергать какой-то дивный экшн перед снятием скриншота.
     */
    actions?: [];

}

export interface TestConfigSkipMode extends TestConfigBase {
    /**
     * Скипает тест для темной темы
     */
    skipDarkMode?: boolean;
}

export interface TestItem extends TestConfigSkipMode {
    id: string;
    group: number;
}

export interface TestCase extends TestConfigSkipMode {
    /**
     * Условие на данные для теста. (Будет создан тест id, если condition true)
     */
    condition(data: unknown): boolean;
}

export interface TestConfig {
    /**
     * высота скриншота
     */
    height?: number;
    /**
     * Скипает тест. Нужно прокомментировать причину скипа.
     */
    skip?: boolean;

    /**
     * Запускает только этот тест. Удобно при разработке.
     */
    only?: boolean;

    /**
     * Скипает тест для темной темы
     */
    skipDarkMode?: boolean;

    /**
     * Сценарии для тестов.
     */
    cases?: TestCase[];
}
