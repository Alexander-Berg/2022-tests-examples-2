TMP="/tmp/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$TMP"/opt

function copy_folder {
    cp -rf "$1" "$TMP/$1"
}

# Копируем тестовые данные
copy_folder "/opt/clickhouse-input/"
copy_folder "/opt/mobile_reports_storage/"
copy_folder "/opt/mobmet_log/"
copy_folder "/opt/infected_masks/"

# Делаем дамп MySQL
mysqldump -h localhost -P 3306 -umetrika -pmetrika --add-drop-database --databases conv_main mobile mobile_redirect_b2b mobile_logs_api > "$TMP/mysql.sql"

# Создаем архив
tar -zcvf /tmp/data.tar.gz -C "$TMP" .
