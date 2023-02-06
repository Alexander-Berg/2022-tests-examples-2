-- Финальное обновление БД после выкатки кода

-- Перед миграцией необходимо убедиться, что все строки в таблицах 'places' и 'delivery_zones'
-- обновлены в соответствии с новым форматом

-- Делаем новые столбцы обязательными (вне транзакции чтобы долго не держать лок)
ALTER TABLE storage.places
    ALTER COLUMN working_intervals SET NOT NULL,
    ALTER COLUMN allowed_couriers_types SET NOT NULL;

BEGIN;
-- В проде в таблицу зон идут 15 RPS на запись и таймаута 1s не хватает:
SET LOCAL lock_timeout='3s';
-- Делаем новые столбцы обязательными и удаляем столбец polygon
ALTER TABLE storage.delivery_zones
    DROP COLUMN source_id,
    DROP COLUMN polygon,
    ALTER COLUMN source SET NOT NULL,
    ALTER COLUMN external_id SET NOT NULL,
    ALTER COLUMN polygons SET NOT NULL;
COMMIT;

-- Добавляем индекс по источнику и внешнему ID
CREATE UNIQUE INDEX CONCURRENTLY ux__delivery_zones__source__external_id
    ON storage.delivery_zones(source, external_id);
