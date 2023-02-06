-- Скрипт для формирования отчета по количеству аккаунтов в каждом консюмере
select tag_table.tag, count(*) as exact_count
from user_tags_table
         inner join tag_table
                    on user_tags_table.tag_id = tag_table.tag_id
where tag_table.tag like 'tus_consumer_value%'
group by tag_table.tag;

select right(tag_table.tag, -length('tus_consumer_value=')), count(*) as exact_count
from user_tags_table
         inner join tag_table
                    on user_tags_table.tag_id = tag_table.tag_id
where tag_table.tag like 'tus_consumer_value%'
group by tag_table.tag;
