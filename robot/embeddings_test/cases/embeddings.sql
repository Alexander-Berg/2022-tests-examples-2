/* syntax version 1 */

$titleKey = AsStruct("PN_Common#OT_Text" as ObjectType, "PN_News#CT_NewsTitle" as CounterType, "RT_Sum" as Reducer);
$textKey = AsStruct("PN_Common#OT_Text" as ObjectType, "PN_News#CT_NewsText" as CounterType, "RT_Sum" as Reducer);


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
    RETURN AsStruct(
        $BuildProfile($title, $text) as Profile,
        $titleKey as Title,
        $textKey as Text
    );
};


$PrintOutput = ($output) -> {
    RETURN DJ::ProfileToStruct(DJ::ProfileFromProto($output.Profile));
};


$Embeddings = DjTools::Embeddings(FolderPath("data"), AsStruct(True as TestMode));


SELECT $PrintOutput($Embeddings($BuildFullInput(Title, Text)))
FROM Input;
