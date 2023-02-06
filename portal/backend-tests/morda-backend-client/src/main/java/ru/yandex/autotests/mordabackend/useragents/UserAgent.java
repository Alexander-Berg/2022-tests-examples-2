package ru.yandex.autotests.mordabackend.useragents;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.02.14
 */
public enum UserAgent {
    FF_23("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:23.0) Gecko/20100101 Firefox/23.0",
            null, null, "Gecko", "23.0", "Firefox", "23.0", "MacOS", "Mac OS X Mavericks", "10.9",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    FF_34("5515777fd5bc2bae0a63d66f",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:34.0) Gecko/20100101 Firefox/34.0",
            null, null, "Gecko", "34.0", "Firefox", "34.0", "MacOS", "Mac OS X Mavericks", "10.9",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    PDA("551577b8d5bc2bae0a63d670",
            "Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.334; U; id) Presto/2.5.25 Version/10.54",
            null, null, "Presto", "2.5.25", "OperaMini", "9.80", "Symbian", null, null,
            0, 1, 1, 0, 0, 0, 0, 0, 0, 0),
    TOUCH("551577d8d5bc2bae0a63d671",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 " +
            "(KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53",
            "Safari", "9537.53", "WebKit", "537.51.2", "MobileSafari", "7.0", "iOS", null, "7.1.1",
            1, 1, 1, 0, 1, 1, 1, 0, 1, 0),
    FF_WINXP_31("Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
            null, null, "Gecko", "31.0", "Firefox", "31.0", "Windows", "Windows XP", "5.1",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    FF_WIN7_29("Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0",
            null, null, "Gecko", "25.0", "Firefox", "29.0", "Windows", "Windows 7", "6.1",
            1, 1, 0, 0, 0, 1, 1, 1, 0, 0),
    FF_BSD_28("Mozilla/5.0 (X11; OpenBSD amd64; rv:28.0) Gecko/20100101 Firefox/28.0",
            null, null, "Gecko", "28.0", "Firefox", "28.0", "OpenBSD", null, null,
            1, 1, 0, 0, 0, 1, 1, 1, 0, 0),
    FF_LINUX_28("Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0",
            null, null, "Gecko", "28.0", "Firefox", "28.0", "Linux", null, null,
            1, 1, 0, 0, 0, 1, 1, 1, 0, 0),
    FF_LINUX_4("Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.3) Gecko/20091020 Ubuntu/10.04 (lucid) Firefox/4.0.1",
            null, null, "Gecko", "1.9.1.3", "Firefox", "4.0", "Linux", "Ubuntu", "10.04",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    CHROME_WIN8_37("Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/37.0.2049.0 Safari/537.36",
            "Chromium", "37.0.2049.0", "WebKit", "537.36", "Chrome", "37.0.2049", "Windows", "Windows 8.1", "6.3",
            1, 1, 0, 0, 0, 1, 1, 1, 0, 0),
    CHROME_WIN7_36("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/36.0.1985.67 Safari/537.36",
            "Chromium", "36.0.1985.67", "WebKit", "537.36", "Chrome", "36.0.1985", "Windows", "Windows 7", "6.1",
            1, 1, 0, 0, 0, 1, 1, 1, 0, 0),
    CHROME_WINXP_36("Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/36.0.1985.67 Safari/537.36",
            "Chromium", "36.0.1985.67", "WebKit", "537.36", "Chrome", "36.0.1985", "Windows", "Windows XP", "5.1",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    CHROME_OSX_36("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/36.0.1944.0 Safari/537.36",
            "Chromium", "36.0.1944.0", "WebKit", "537.36", "Chrome", "36.0.1944",
            "MacOS", "Mac OS X Mavericks", "10.9.2",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    CHROME_OSX_35("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/35.0.1916.47 Safari/537.36",
            "Chromium", "35.0.1916.47", "WebKit", "537.36", "Chrome", "35.0.1916",
            "MacOS", "Mac OS X Mavericks", "10.9.3",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    CHROME_WINXP_34("Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/34.0.1847.116 Safari/537.36",
            "Chromium", "34.0.1847.116", "WebKit", "537.36", "Chrome", "34.0.1847", "Windows", "Windows XP", "5.1",
            1, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    IOS_IPAD("Mozilla/5.0 (iPad; CPU OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) " +
            "Version/8.0 Mobile/12A4345d Safari/600.1.4",
            "Safari", "600.1.4", "WebKit", "600.1.4", "MobileSafari", "8.0", "iOS", null, "8.1.1",
            1, 1, 1, 1, 1, 1, 1, 0, 1, 0),
    ANDROID_LG("Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) " +
            "AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Safari", "534.30", "WebKit", "534.30", "AndroidBrowser", "4.0",
            "Android", "Android Ice Cream Sandwich", "4.0.3",
            1, 1, 1, 0, 1, 1, 1, 0, 1, 0),
    ANDROID_SAMS_TAB("Mozilla/5.0 (Linux; U; Android 4.2.2; nl-nl; SM-T310 Build/JDQ39) " +
            "AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30",
            "Safari", "534.30", "WebKit", "534.30", "AndroidBrowser", "4.0",
            "Android", "Android Jelly Bean", "4.2.2",
            1, 1, 1, 1, 1, 1, 1, 0, 1, 0),
    ANDROID_HTC_SENS("5515781fd5bc2bae0a63d673",
            "Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K) " +
            "AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "Safari", "534.30", "WebKit", "534.30", "AndroidBrowser", "4.0",
            "Android", "Android Ice Cream Sandwich", "4.0.3",
            1, 1, 1, 0, 1, 1, 1, 0, 1, 0),
    SAFARI_ANDROID("Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9",
            "Safari", "999.9", "WebKit", "999", "AndroidBrowser", null, "Android", "Android Gingerbread", "2.3",
            1, 1, 1, 0, 1, 1, 1, 0, 1, 0),
    ANDROID_HTC_INCR("Mozilla/5.0 (Linux; U; Android 2.3.5; zh-cn; HTC_IncredibleS_S710e Build/GRJ90) " +
            "AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            "Safari", "533.1", "WebKit", "533.1", "AndroidBrowser", "4.0",
            "Android", "Android Gingerbread", "2.3.5",
            1, 1, 1, 0, 1, 1, 1, 0, 1, 0),
    BLACKBERRY_9900("Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en) AppleWebKit/534.11+ (KHTML, like Gecko) " +
            "Version/7.1.0.346 Mobile Safari/534.11+",
            "Safari", "534.11", "WebKit", "534.11", "BlackBerry", "7.1.0", "BlackBerry", null, null,
            1, 1, 1, 0, 0, 1, 1, 0, 1, 0),
    BLACKBERRY_9860("Mozilla/5.0 (BlackBerry; U; BlackBerry 9860; en-US) AppleWebKit/534.11+ (KHTML, like Gecko) " +
            "Version/7.0.0.254 Mobile Safari/534.11+",
            "Safari", "534.11", "WebKit", "534.11", "BlackBerry", "7.0.0", "BlackBerry", null, null,
            1, 1, 1, 0, 0, 1, 1, 0, 1, 0),
    IE_10("Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
            null, null, "Trident", "6.0", "MSIE", "10.0", "Windows", "Windows 7", "6.1",
            1, 1, 0, 0, 0, 1, 1, 1, 0, 0),
    IE_9("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)",
            null, null, "Trident", "5.0", "MSIE", "9.0", "Windows", null, "7.1",
            0, 1, 0, 0, 0, 1, 1, 0, 0, 0),
    IE_8("Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; " +
            "InfoPath.1; SV1; .NET CLR 3.8.36217; WOW64; en-US)",
            null, null, "Trident", "4.0", "MSIE", "8.0", "Windows", "Windows Vista", "6.0",
            0, 1, 0, 0, 0, 1, 1, 1, 0, 0),
    IE_7("Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 6.0; en-US)",
            null, null, "Trident", null, "MSIE", "7.0", "Windows", "Windows Vista", "6.0",
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0),
    IE_6("Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",
            null, null, "Trident", null, "MSIE", "6.0", "Windows", "Windows XP", "5.1",
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0),
    FF_ANDROID("Mozilla/5.0 (Android; Linux armv7l; rv:9.0) Gecko/20111216 Firefox/9.0 Fennec/9.0",
            null, null, "Gecko", "9.0", "MobileFirefox", "9.0", "Android", null, null,
            0, 1, 1, 0, 1, 0, 0, 0, 1, 0),
    MAEMO("Mozilla/5.0 (X11; U; Linux armv7l; ru-RU; rv:1.9.2.3pre) Gecko/20100723 Firefox/3.5 " +
            "Maemo Browser 1.7.4.8 RX-51 N900",
            null, null, "Gecko", "1.9.2.3", "MobileFirefox", "3.5", "MeeGo", null, null,
            0, 1, 1, 0, 1, 0, 0, 0, 1, 0),
    OPERA_MINI("Opera/9.80 (J2ME/MIDP; Opera Mini/5.1.22296/22.87; U; fr) Presto/2.5.25",
            null, null, "Presto", "2.5.25", "OperaMini", "5.1", "Java", null, null,
            0, 1, 1, 0, 0, 0, 0, 0, 0, 0),
    CURL("curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)",
            null, null, null, null, null, null, "Linux", null, null,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    YABRO_ANDROID("Mozilla/5.0 (Linux; Android 4.1.1; xDevice_Note_II_6.0 Build/IMM76D) " +
            "AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 YaBrowser/1.0.1364.172 Mobile Safari/537.22",
            "Chromium", "25.0.1364.172", "WebKit", "537.22", "YandexBrowser", "1.0.1364.172",
            "Android", "Android Jelly Bean", "4.1.1",
            1, 1, 1, 0, 1, 1, 1, 0, 1, 0),
    APACHE_HTTPCLIENT("Apache-HttpClient/4.0.3 (java 1.5)",
            null, null, "Unknown", null, "Unknown", null, "Unknown", null, null,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    WP8("55157801d5bc2bae0a63d672",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 920)",
            null, null, "Trident", "6.0", "IEMobile", "10.0", "WindowsPhone", null, "8.0",
            1, 1, 1, 0, 1, 1, 1, 0, 0, 0);

    private String value;

    private String browserBase;
    private String browserBaseVersion;
    private String browserEngine;
    private String browserEngineVersion;
    private String browserName;
    private String browserVersion;
    private String OSFamily;
    private String OSName;
    private String OSVersion;
    private int historySupport;
    private int isBrowser;
    private int isMobile;
    private int isTablet;
    private int isTouch;
    private int localStorageSupport;
    private int postMessageSupport;
    private int x64;
    private int multiTouch;
    private int inAppBrowser;
    private String mongoId;

    UserAgent(String value, String browserBase, String browserBaseVersion, String browserEngine,
              String browserEngineVersion, String browserName, String browserVersion, String OSFamily,
              String OSName, String OSVersion, int historySupport, int isBrowser, int isMobile, int isTablet,
              int isTouch, int localStorageSupport, int postMessageSupport, int x64, int multiTouch, int inAppBrowser) {
        this("", value, browserBase, browserBaseVersion, browserEngine, browserEngineVersion, browserName,
                browserVersion, OSFamily, OSName, OSVersion, historySupport, isBrowser, isMobile, isTablet,
                isTouch, localStorageSupport, postMessageSupport, x64, multiTouch, inAppBrowser);

    }

    UserAgent(String mongoId, String value, String browserBase, String browserBaseVersion, String browserEngine,
              String browserEngineVersion, String browserName, String browserVersion, String OSFamily,
              String OSName, String OSVersion, int historySupport, int isBrowser, int isMobile, int isTablet,
              int isTouch, int localStorageSupport, int postMessageSupport, int x64, int multiTouch, int inAppBrowser) {
        this.mongoId = mongoId;
        this.value = value;
        this.browserBase = browserBase;
        this.browserBaseVersion = browserBaseVersion;
        this.browserEngine = browserEngine;
        this.browserEngineVersion = browserEngineVersion;
        this.browserName = browserName;
        this.browserVersion = browserVersion;
        this.OSFamily = OSFamily;
        this.OSName = OSName;
        this.OSVersion = OSVersion;
        this.historySupport = historySupport;
        this.isBrowser = isBrowser;
        this.isMobile = isMobile;
        this.isTablet = isTablet;
        this.isTouch = isTouch;
        this.localStorageSupport = localStorageSupport;
        this.postMessageSupport = postMessageSupport;
        this.x64 = x64;
        this.multiTouch = multiTouch;
        this.inAppBrowser = inAppBrowser;
    }

    public String getValue() {
        return value;
    }

    public String getBrowserBase() {
        return browserBase;
    }

    public String getBrowserBaseVersion() {
        return browserBaseVersion;
    }

    public String getBrowserEngine() {
        return browserEngine;
    }

    public String getBrowserEngineVersion() {
        return browserEngineVersion;
    }

    public String getBrowserName() {
        return browserName;
    }

    public String getBrowserVersion() {
        return browserVersion;
    }

    public String getOSFamily() {
        return OSFamily;
    }

    public String getOSName() {
        return OSName;
    }

    public String getOSVersion() {
        return OSVersion;
    }

    public int getHistorySupport() {
        return historySupport;
    }

    public int getIsBrowser() {
        return isBrowser;
    }

    public int getIsMobile() {
        return isMobile;
    }

    public boolean isMobile() {
        return isMobile == 1;
    }

    public int getIsTablet() {
        return isTablet;
    }

    public int getIsTouch() {
        return isTouch;
    }

    public int getLocalStorageSupport() {
        return localStorageSupport;
    }

    public int getPostMessageSupport() {
        return postMessageSupport;
    }

    public int getX64() {
        return x64;
    }

    public int getMultiTouch() {
        return multiTouch;
    }

    public int getInAppBrowser() {
        return inAppBrowser;
    }

    public String getMongoId() {
        return mongoId;
    }
}
