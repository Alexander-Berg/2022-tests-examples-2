package ru.yandex.price_calc_testapp;

import android.util.Base64;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

import ru.yandex.pricecalc.CompositePrice;
import ru.yandex.pricecalc.MovementPoint;
import ru.yandex.pricecalc.TripDetails;

public class TestData {
    public static final double DOUBLE_EPSILON = 1e-10;

    public static final ArrayList<MovementPoint> ROUTE = new ArrayList<>(Arrays.asList(
            new MovementPoint(4, 6, 0, 0),
            new MovementPoint(5, 4, 30, 3),
            new MovementPoint(7, 6, 60, 6),
            new MovementPoint(8, 5, 80, 8),
            new MovementPoint(11, 5, 100, 10),
            new MovementPoint(10, 7, 150, 50),
            new MovementPoint(8, 8, 160, 51),
            new MovementPoint(16, 7, 200, 80),
            new MovementPoint(8.5, 5.5, 202, 83),
            new MovementPoint(3, 7, 275, 130),
            new MovementPoint(7, 4, 400, 200)
    ));

    public static final ArrayList<MovementPoint> ROUTE_HELSINKI = new ArrayList<>(Arrays.asList(
            new MovementPoint(24.935541, 60.162660, 0, 0),
            new MovementPoint(24.935541, 60.162660, 2000, 240)
    ));

    private static final List<String> POLYGONS_B64 = new ArrayList<>(Arrays.asList(
            "AAAACGdlb2FyZWEyAAAAA0AcAAAAAAAAQBQAAAAAAABAJAAAAAAAAEAiAAAAAAAAQCoAAAAAAABAAAAAAAAAAEAkAAAAAAAA",
            "AAAACGdlb2FyZWExAAAABEAAAAAAAAAAQCAAAAAAAABAEAAAAAAAAEAAAAAAAAAAQCIAAAAAAABAEAAAAAAAAEAiAAAAAAAAQBgAAAAAAABAPgAAAAAAAA=="
    ));

    public static final ArrayList<ArrayList<Byte>> POLYGONS = new ArrayList<ArrayList<Byte>>();
    static {
        for (final String polygonB64 : POLYGONS_B64) {
            POLYGONS.add(fromArray(Base64.decode(polygonB64, Base64.DEFAULT)));
        }
    }

    private static final List<String> POLYGONS_HELSINKI_B64 = new ArrayList<>(Arrays.asList(
            "AAAACGhlbHNpbmtpAAAAI0A4pbtf8u9sQE4TseqnZvJAOKEq7R1LT0BOHYlKSYaWQDjIv69PBW1ATh2L3YBxEkA40ZFxgL9kQE4fzpErOS9AOM2YrR1LX0BOI3R18LpuQDjdZmi512VATiXbTmGFPkA455UYjmzDQE4fn8FFyzZAOOcq36HcXkBOHf/4q3TJQDjomSa1TBVATh1hb8EdXkA46R2qPwPdQE4cQbQFFHtAOOhnLci7tUBOGyHkfJwmQDjqDUU6kN1AThhuoyUWKUA47CPcrGYHQE4Yy2kgszpAOOrLRqB0oUBOGt7t5Z1wQDjsFbCUg1NAThyYpeLje0A46aPaiJH3QE4fORG+9iBAOOtFJQWVmkBOIOy9I80AQDjxpW+CmURATiKapIcSp0A49ezH7G1gQE4kc+snBYFAOP/F7y6R+EBOJqwnMuEjQDkACpZwtpZATilIhFL+4kA5Drk9sts3QE4sOBhqX35AOSA35PT/4kBOLBVJJgfvQDkWoKWu869ATiK+jYY6h0A5JfZ7bG7fQE4fdmMo9G9AOTMDUSnqBkBOG7JsqWoZQDkxph9fBFVAThiQfV7MUUA5GEpBJFyHQE4UcbYiFmlAOQ5+IL6NlkBOFDdkIR3yQDj4NwBYvoNAThQISHogVkA47N3YP0q7QE4SeX/zIIZAOORUsCXW/EBOEn6MKzBCQDjLGIgMYzdAThOAAP8du0A4tFJf8u91QE4SOhqjX5ZAOKW7X/LvbEBOE7Hqp2byP7Azu3ewg5w="
    ));
    public static final ArrayList<ArrayList<Byte>> POLYGONS_HELSINKI = new ArrayList<ArrayList<Byte>>();
    static {
        for (final String polygonB64 : POLYGONS_HELSINKI_B64) {
            POLYGONS_HELSINKI.add(fromArray(Base64.decode(polygonB64, Base64.DEFAULT)));
        }
    }

    private static final String PRICES_1_B64 = "QFvGZmZmZmYAAAAAAAAAAAAAAAMAAAAIZ2VvYXJlYTEAAAABQE4AAAAAAAB/8AAAAAAAAD/QAAAAAAAAAAAAAUAmAAAAAAAAf/AAAAAAAAA/tHrhR64UewAAAAhnZW9hcmVhMgAAAAEAAAAAAAAAAH/wAAAAAAAAP+ZmZmZmZmYAAAADQDQAAAAAAABATgAAAAAAAD/szMzMzMzNQE4AAAAAAABAWQAAAAAAAD/pmZmZmZmaQFuAAAAAAABAXgAAAAAAAD/jMzMzMzMzAAAABnN1YnVyYgAAAAJANAAAAAAAAEBnwAAAAAAAP9MzMzMzMzNAZ8AAAAAAAH/wAAAAAAAAP8mZmZmZmZoAAAAA";
    private static final String PRICES_2_B64 = "QFvGZmZmZmZAiQAAAAAAAAAAAAMAAAAIZ2VvYXJlYTEAAAABQE4AAAAAAAB/8AAAAAAAAD/QAAAAAAAAAAAAAUAmAAAAAAAAf/AAAAAAAAA/tHrhR64UewAAAAhnZW9hcmVhMgAAAAEAAAAAAAAAAH/wAAAAAAAAP+ZmZmZmZmYAAAADQDQAAAAAAABATgAAAAAAAD/szMzMzMzNQE4AAAAAAABAWQAAAAAAAD/pmZmZmZmaQFuAAAAAAABAXgAAAAAAAD/jMzMzMzMzAAAABnN1YnVyYgAAAAJANAAAAAAAAEBnwAAAAAAAP9MzMzMzMzNAZ8AAAAAAAH/wAAAAAAAAP8mZmZmZmZoAAAAAQHQYAAAAAABAl3AAAAAAAAAAAAFANAAAAAAAAH/wAAAAAAAAP9zMzMzMzM0AAAABQC4AAAAAAAB/8AAAAAAAAD/VHrhR64Uf";
    private static final String PRICES_HELSINKI_B64 = "QAgAAAAAAAAAAAAAAAAAAAAAAAIAAAAIaGVsc2lua2kAAAABQI9AAAAAAAB/8AAAAAAAAD9SBbwBo24vAAAAAkBmgAAAAAAAQIDgAAAAAAA/a06BtOgbT0CA4AAAAAAAf/AAAAAAAAA/d+SxfksX5AAAAAZzdWJ1cmIAAAABAAAAAAAAAAB/8AAAAAAAAD9VTJhfBvaUAAAAAgAAAAAAAAAAQIDgAAAAAAA/a06BtOgbT0CA4AAAAAAAf/AAAAAAAAA/d+SxfksX5A==";

    public static final ArrayList<Byte> PRICES_1 = fromArray(Base64.decode(PRICES_1_B64, Base64.DEFAULT));
    public static final ArrayList<Byte> PRICES_2 = fromArray(Base64.decode(PRICES_2_B64, Base64.DEFAULT));
    public static final ArrayList<Byte> PRICES_HELSINKI = fromArray(Base64.decode(PRICES_HELSINKI_B64, Base64.DEFAULT));

    public static final CompositePrice PRICE_1 = new CompositePrice(111.1, 154.75, 53.1, 0.0, 0.0, 0.0, 0.0);
    public static final CompositePrice PRICE_2 = new CompositePrice(871.1950140005421, 463.3727757203505, 165.43221027910758, 0.0, 0.0, 0.0, 0.0);
    public static final CompositePrice PRICE_HELSINKI = new CompositePrice(3, 1.1, 0.2, 0, 0, 0.0, 0.0);

    public static final CompositePrice PRICE = new CompositePrice(10.3, 543.2, 457.44, 78.0, 0.0, 0.0, 0.0);
    public static final CompositePrice PRICE_x_0_9 = new CompositePrice(
            PRICE.getBoarding() * 0.9,
            PRICE.getDistance() * 0.9,
            PRICE.getTime() * 0.9,
            PRICE.getWaiting() * 0.9,
            PRICE.getRequirements() * 0.9,
            PRICE.getTransitWaiting() * 0.9,
            PRICE.getDestinationWaiting() * 0.9
    );
    public static final CompositePrice PRICE_REQ_PLUS_3x42 = new CompositePrice(
            PRICE.getBoarding(),
            PRICE.getDistance(),
            PRICE.getTime(),
            PRICE.getWaiting(),
            PRICE.getRequirements() + 3 * 42,
            PRICE.getTransitWaiting(),
            PRICE.getDestinationWaiting()
    );

    public static final double PRICE_SUM = PRICE.getBoarding() + PRICE.getDistance() + PRICE.getTime()
            + PRICE.getWaiting() + PRICE.getRequirements() + PRICE.getTransitWaiting() + PRICE.getDestinationWaiting();

    public static final TripDetails TRIP_DETAILS = new TripDetails(
            11203,
            6053,
            430,
            0,
            0,
            new HashMap<String, Double>() {{
                put("paid_option", 3.0);
                put("cup_of_coffee", 1.0);
                put("piece_of_cake", 6.0);
            }}
    );

    // bytecode for "return price * 0.9;"
    public static final ArrayList<Byte> BYTECODE_return_price_x_0_9 = new ArrayList<>(Arrays.asList(
            (byte) 0x13, (byte) 0x11, (byte) 0x3f, (byte) 0xec, (byte) 0xcc, (byte) 0xcc, (byte) 0xcc,
            (byte) 0xcc, (byte) 0xcc, (byte) 0xcd, (byte) 0x22, (byte) 0x80
    ));

    public static final ArrayList<Byte> BYTECODE_WITH_EMIT = new ArrayList<>(Arrays.asList(
            (byte) 0x13, (byte) 0x82, (byte) 0x00, (byte) 0x01, (byte) 0x15, (byte) 0x01, (byte) 0x83,
            (byte) 0x00, (byte) 0x01, (byte) 0x15, (byte) 0x01, (byte) 0x80
    ));

    /* bytecode for:
        return {
          requirements = ("paid_option" in ride.ride.user_options)
                             ? ride.ride.user_options["paid_option"] * 42
                             : ride.price.requirements
        };
    */
    public static final ArrayList<Byte> BYTECODE_if_paid_option_in_user_options = new ArrayList<>(Arrays.asList(
            (byte) 0x14, (byte) 0x00, (byte) 0x14, (byte) 0x01, (byte) 0x14, (byte) 0x02, (byte) 0x14,
            (byte) 0x03, (byte) 0x16, (byte) 0x00, (byte) 0x0b, (byte) 0x70, (byte) 0x61, (byte) 0x69,
            (byte) 0x64, (byte) 0x5f, (byte) 0x6f, (byte) 0x70, (byte) 0x74, (byte) 0x69, (byte) 0x6f,
            (byte) 0x6e, (byte) 0x12, (byte) 0x05, (byte) 0x90, (byte) 0x12, (byte) 0x05, (byte) 0x16,
            (byte) 0x00, (byte) 0x0b, (byte) 0x70, (byte) 0x61, (byte) 0x69, (byte) 0x64, (byte) 0x5f,
            (byte) 0x6f, (byte) 0x70, (byte) 0x74, (byte) 0x69, (byte) 0x6f, (byte) 0x6e, (byte) 0x91,
            (byte) 0x11, (byte) 0x40, (byte) 0x45, (byte) 0x00, (byte) 0x00, (byte) 0x00, (byte) 0x00,
            (byte) 0x00, (byte) 0x00, (byte) 0x22, (byte) 0x14, (byte) 0x04, (byte) 0x00, (byte) 0x14,
            (byte) 0x05, (byte) 0x14, (byte) 0x06, (byte) 0x81
    ));

    private static ArrayList<Byte> fromArray(byte[] bytes) {
        ArrayList<Byte> list = new ArrayList<>();
        for (byte b : bytes) list.add(b);
        return list;
    }
}
