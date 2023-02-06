/* syntax version 1 */

$titleKey = AsStruct("PN_Common#OT_Text" as ObjectType, "PN_News#CT_NewsTitle" as CounterType, "RT_Sum" as Reducer);
$textKey = AsStruct("PN_Common#OT_Text" as ObjectType, "PN_News#CT_NewsText" as CounterType, "RT_Sum" as Reducer);
$outputKeys = AsStruct("PN_Common#OT_Keyword" as ObjectType, "PN_News#CT_TrafficNewsVisits" as CounterType, AsList("RT_Sum_7d", "RT_Sum_30d") as Reducers);


$AddCounter = ($profile, $key, $text) -> {
    RETURN DJ::AddProfileCounters(
        $profile,
        AsList(
            ExpandStruct(
                $key,
                $text as ObjectId,
                CAST(1 as Float) as Value,
                Unwrap(CAST(0 as Uint32)) as Timestamp
            )
        )
    );
};

$BuildProfile = ($title, $text) -> {
    $profile = DJ::EmptyProfile();
    $profile = IF($title IS NULL, $profile, $AddCounter($profile, $titleKey, Unwrap($title)));
    $profile = IF($text IS NULL, $profile, $AddCounter($profile, $textKey, Unwrap($text)));
    RETURN DJ::ProfileToProto($profile);
};


$BuildFullInput = ($title, $text) -> {
    RETURN ExpandStruct(
        $outputKeys,
        $BuildProfile($title, $text) as Profile,
        $titleKey as Title,
        $textKey as Text
    );
};

$BuildSingleInput = ($title, $text) -> {
    RETURN ExpandStruct(
        $outputKeys,
        $BuildProfile($title, $text) as Profile,
        $textKey as Text
    );
};


$PrintOutput = ($output) -> {
    RETURN DJ::ProfileToStruct(DJ::ProfileFromProto($output.Profile));
};


$Keywords = DjTools::Keywords(FolderPath("data"), AsStruct(True as TestMode));


SELECT $PrintOutput($Keywords($BuildFullInput(Title, Text)))
FROM Input;

SELECT $PrintOutput($Keywords($BuildSingleInput(Title, Text)))
FROM Input;
