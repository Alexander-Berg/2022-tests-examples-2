package ru.yandex.autotests.morda.pages;

public class MordaEnvironment {
    private String prefix;
    private String environment;

    private MordaEnvironment(String prefix, String environment) {
        this.prefix = prefix;
        this.environment = environment;
    }

    public static MordaEnvironment mordaEnvironment(String prefix, String environment) {
        return new MordaEnvironment(prefix, environment);
    }

    public String getPrefix() {
        return prefix;
    }

    public String getEnvironment() {
        return environment;
    }

    public String parse() {
        if (environment == null || environment.isEmpty()) {
            throw new IllegalArgumentException("Environment must not be null or empty");
        }

        if (environment.equals("production")) {
            return prefix + ".";
        }

        if (environment.equals("serp")) {
            return "";
        }

        return prefix + "-" + environment + ".";
    }
}
