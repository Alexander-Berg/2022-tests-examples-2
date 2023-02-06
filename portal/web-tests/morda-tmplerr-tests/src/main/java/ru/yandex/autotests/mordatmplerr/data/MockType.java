package ru.yandex.autotests.mordatmplerr.data;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.03.14
 */
public enum MockType {
    BIG("big"),
    TOUCH("touch"),
    PDA("pda");

    private String name;

    private MockType(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public static MockType getMockType(String type) {
        for (MockType mockType : MockType.values()) {
            if (mockType.getName().equals(type)) {
                return mockType;
            }
        }
        throw new RuntimeException("MockType " + type + " is unknown");
    }
}
