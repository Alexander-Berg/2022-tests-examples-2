SELECT user_table.uid,
       user_table.login,
       user_table.password,
       user_table.locked_until,
       user_table.delete_at
FROM user_table
         JOIN consumer_test_accounts_table
              ON user_table.uid = consumer_test_accounts_table.uid
WHERE user_table.uid = :uid
  AND consumer_test_accounts_table.consumer_name IN (
    SELECT consumer_name
    FROM consumer_clients_table
    WHERE login = :client_login
);


SELECT user_table.uid,
       user_table.login,
       user_table.password,
       user_table.locked_until,
       user_table.delete_at
FROM user_table
         JOIN consumer_test_accounts_table
              ON user_table.uid = consumer_test_accounts_table.uid
WHERE user_table.login = :login
  AND consumer_test_accounts_table.consumer_name IN (
    SELECT consumer_name FROM consumer_clients_table WHERE login = :client_login
);

SELECT user_table.uid,
       user_table.login,
       user_table.password,
       user_table.locked_until,
       user_table.delete_at
FROM user_table
         JOIN consumer_test_accounts_table
              ON user_table.uid = consumer_test_accounts_table.uid
WHERE consumer_test_accounts_table.consumer_name IN (
    SELECT consumer_name FROM consumer_clients_table WHERE login = :client_login
)
  AND user_table.uid IN (
    SELECT user_tags_table.uid
    FROM user_tags_table
             JOIN tag_table
                  ON user_tags_table.tag_id = tag_table.tag_id
    WHERE tag_table.tag in :tags
    GROUP BY user_tags_table.uid
    HAVING count(DISTINCT user_tags_table.tag_id) = :tags_length
)
  AND user_table.locked_until < :expiration_time
LIMIT 100;
