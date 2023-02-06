mkdir -p ./services/geo-pipeline-control-plane/testsuite/static2
for file in bad_configs_create.json bad_configs.json config1.json config2.json db_geo_pipeline_configs_test.json db_geo_pipeline_configs_empty.json
do
    python3 ./libraries/geo-pipeline-config/scripts/migration/v2_v3.py ./services/geo-pipeline-control-plane/testsuite/static_t/$file ./services/geo-pipeline-control-plane/testsuite/static2/$file
done
