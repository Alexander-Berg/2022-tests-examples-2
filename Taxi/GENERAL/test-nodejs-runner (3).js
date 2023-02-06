/**
 * Тестовый скрипт для проверки запуска скриптов nodejs
 * https://a.yandex-team.ru/arc_vcs/taxi/backend-py3/services/scripts/debian/scripts-executors/nodejs_request_script.py
 */

console.log('ARGUMENTS:', process.argv);

if (process.argv.includes('--err')) {
    console.log('Throwing test error');
    throw new Error('Test Error');
}
