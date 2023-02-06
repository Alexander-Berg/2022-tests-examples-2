package ru.yandex.audience.uploading.crm;

import java.util.List;

import com.google.common.collect.ImmutableList;

public class SampleCrmData {

    public static final String HEADER = "phone,email,data";
    public static final List<String> VALID_DATA = ImmutableList.of(
            HEADER,
            "666,email@example.com,client",
            "777,chuknorris@everywhere.com,\"no info\""
    );

    public static final List<String> VALID_HASHED_DATA = ImmutableList.of(
            HEADER,
            "302c493ba08cebae2624f16dda33ae61,7815696ecbf1c96e6894b779456d330e,client",
            "a8f5f167f44f4964e6c998dee827110c,97cec346b6e141b23c8d0d0e4bfc42f7,\"no info\""
    );

    public static final String BOM = "\uFEFF";

    public static final List<String> VALID_HASHED_DATA_BOM = ImmutableList.of(
            BOM + HEADER,
            "302c493ba08cebae2624f16dda33ae61,7815696ecbf1c96e6894b779456d330e,client",
            "a8f5f167f44f4964e6c998dee827110c,97cec346b6e141b23c8d0d0e4bfc42f7,\"no info\""
    );


    public static final List<String> INVALID_DATA = ImmutableList.of(
            "phone,email",
            "bad-phone,bad-email_!"
    );
}
