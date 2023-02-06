yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/scripts.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01d4qfywjg815vxxzmahs3efb9->API_ADMIN_SERVICES_TOKENS
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01ct1ak1amgqnb1kmb8q82th9n->STARTRACK_API_TOKEN
        - sec-01d40tjb6g6sg88a4243rmq57s->ADMIN_SCRIPT_LOGS_MDS_S3
        - sec-01dabdxtbvmywzk8grgjv4qx9q->TVM_TAXI_SCRIPTS
        - sec-01dabczyqb33ajvg36v00tkztv->TVM_TAXI_APPROVALS
        - sec-01dj8bnnezgrnvw2vh72e8wnw7->EDA_BB_AUTH_TOKEN
        - sec-01f4eb89jbxe99ca8xvwv36qa1->API_TOKEN_TAXI_SCRIPTS_ARC
        - sec-01fnbpwfs99jqepd14vk3ycjjq->S3MDS_TAXI_SCRIPTS_ARCHIVE
      vars:
        - ST_URL: "https://st-api.test.yandex-team.ru/v2/"
