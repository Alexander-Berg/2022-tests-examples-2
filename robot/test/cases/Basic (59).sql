/* syntax version 1 */
$forum = Prewalrus::Forum();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $forumResult = $forum(
        $numeratorResult.NumeratorEvents,
        $row.Url,
        $row.Language,
        $row.LastAccess
    );

    return AsStruct(
        $row.Url AS Url,
        $forumResult.FirstPostDate AS FirstPostDate,
        $forumResult.LastPostDate AS LastPostDate,
        $forumResult.NumForumPosts AS NumForumPosts,
        $forumResult.NumForumAuthors AS NumForumAuthors,
        $forumResult.ForumResult AS ForumResult,
        $forumResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

