const {spawn} = require('child_process')

const ROOT_DIR = require('app-root-path').path

/**
 * Стартуем мок-сервер в отдельном процессе
 */
async function startMockServer() {
  return await new Promise((resolve, reject) => {
    const cmd = spawn(`${ROOT_DIR}/tools/command/e2e/run/mock.dev.sh`)

    cmd.stdout.on('data', data => {
      console.log(`[mock-server][log]: ${data}`)

      // ждем от мок сервера сообщение
      // Mock-server listening at http://localhost:7777
      if (data.includes('Mock-server listening at')) {
        resolve(cmd)
      }
    })

    cmd.stderr.on('data', data => {
      console.error(data.toString())
      reject(new Error('Failed to start mock server'))
    })

    cmd.unref()
  })
}

module.exports = async () => {
  global.mockServerProcess = await startMockServer()
}
