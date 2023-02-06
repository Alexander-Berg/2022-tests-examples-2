$processResultOnTestRun = ($url, $result) -> {
    RETURN IF (String::StartsWith($url, 'https://throw-error'),
                AsStruct("error on fetching from db" AS Error),
                $result);
};
