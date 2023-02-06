package ru.yandex.metrika.api.management.client.uploading;

import org.joda.time.LocalDate;

import ru.yandex.metrika.util.time.DateTimeFormatters;

public class ExpenseCsvSampleData {

    private static final String TODAY = DateTimeFormatters.ISO_DTF.print(LocalDate.now());

    public static final String INVALID_DATE = "Date,UTMSource,Expenses\r\n201901-01,facebook,100\r\n";
    public static final String INVALID_DATE_MULTIPLE = "Date,UTMSource,Expenses\r\n" + TODAY + "/2019-02-01/2019-03-01,facebook,100\r\n";
    public static final String INVALID_EXPENSES = "Date,UTMSource,Expenses\r\n" + TODAY + ",facebook,100o\r\n";
    public static final String INVALID_NO_REQUIRED_DATE_COLUMN = "UTMSource,Expenses\r\nfacebook,100\r\n";
    public static final String INVALID_NO_VALUE_IN_REQUIRED_DATE_COLUMN = "UTMSource,Expenses,Date\r\nfacebook,," + TODAY + "\r\n";
    public static final String INVALID_NO_REQUIRED_UTMSOURCE_CSV = "Date,Expenses\r\n" + TODAY + ",100\r\n";
    public static final String INVALID_NO_REQUIRED_UTMSOURCE_AND_EXPENSES_CSV = "Date\r\n" + TODAY + "\r\n";
    public static final String INVALID_NO_REQUIRED_EXPENSES_COLUMN = "Date,UTMSource\r\n" + TODAY + ",facebook\r\n";
    public static final String VALID_DATA = "Date,UTMSource,Expenses\r\n" + TODAY + ",facebook,100\r\n";
    public static final String VALID_DATA_BIG_W_EXTRA_COLUMNS = "UTMSource,UTMMedium,UTMCampaign,ym:CampaignID,ym:keyword,ym:adContent,Expenses,Clicks,ym:impressions,ym:adGroup,ym:adSlot,Date,ym:importBehavior\n" +
            "facebook,cpc,marketingresourcesRU-event,6140111652788,(not set),(not set),3.61,25,623,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6120803086588,(not set),(not set),84.9,227,29108,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook,cpc,analyticsresourcesID-event,6139793235988,(not set),(not set),4.95,21,1609,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook,cpc,marketingresourcesEU-event,6140110428588,(not set),(not set),7.14,28,2519,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook,cpc,analyticsresourcesEU-event,6140110428588,(not set),(not set),7.11,34,2827,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6135866938588,(not set),(not set),28.99,225,13438,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6136072802188,(not set),(not set),29.35,62,4709,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6136072111188,(not set),(not set),29.68,38,2551,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook,cpc,marketingresourcesID-event,6139793235988,(not set),(not set),4.93,22,2121,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6111405747388,(not set),(not set),1.06,5,154,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6121007487588,(not set),(not set),20.19,52,4356,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6111406751988,(not set),(not set),1.1,4,299,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook.com,referral,(not set),6137426628988,(not set),(not set),19.81,73,8874,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "facebook,cpc,analyticsresourcesRU-event,6140111652788,(not set),(not set),3.76,28,1046,46737: facebook via OWOX (2811430452254985) | 42118853,0," + TODAY + ",SUMMATION\n" +
            "criteo,cpc,lowerfunnel,124605,(not set),(not set),762.09146,4663,1069810,47004: criteo via OWOX (mapi-65167123-d343-4d65-80a4-f1ce02ab33f4) | 42234606,0," + TODAY + ",SUMMATION\n" +
            "criteo,cpc,midfunnel,139763,(not set),(not set),22.57859,396,119189,47004: criteo via OWOX (mapi-65167123-d343-4d65-80a4-f1ce02ab33f4) | 42234606,0," + TODAY + ",SUMMATION";

}
