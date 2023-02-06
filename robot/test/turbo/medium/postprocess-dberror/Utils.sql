$processResultOnTestRun = ($url, $result) -> {
    RETURN IF (String::StartsWith($url, 'throw-error.test') OR String::StartsWith($url, 'https://throw-error.test'),
                AsStruct("error on fetching from db" AS Error),
                $result);
};
