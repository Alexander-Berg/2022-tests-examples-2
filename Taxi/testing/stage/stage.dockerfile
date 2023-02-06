#############
#START_FRAGMENT STAGE

# Сюда не надо добавлять ARG. Их нужно добавлять в base.dockerfile
FROM ${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}

RUN mkdir -p /var/www/html

{{CODE_TEMPLATE}}

#END_FRAGMENT
#############
