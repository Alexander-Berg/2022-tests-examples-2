/* Safe for arcadia https://docs.yandex-team.ru/devtools/src/arcadia#filestructure */
const FILE_NAME_MAX_LENGTH = 143
/*  '/s' is not used for more pretty filenames */
// eslint-disable-next-line no-useless-escape
const FILE_NAME_BLACKLIST_REG_EXP = /[^\.\{\}\-,\(\)\[\]\{\}\+=#\$@\!a-zA-Z0-9]/g

export const getSafeArcadiaFileName = (name: string) => {
  return name.trim().replace(FILE_NAME_BLACKLIST_REG_EXP, '_').slice(0, FILE_NAME_MAX_LENGTH)
}
