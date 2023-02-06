/**
 * Убиваем мок-сервер в отдельном процессе
 */
async function stopMockServer() {
  return await new Promise((resolve, reject) => {
    const cmd = global.mockServerProcess

    if (cmd) {
      cmd.stdout.destroy()
      cmd.stderr.destroy()
      try {
        cmd.kill('SIGINT')
      } catch (err) {
        reject(err)
      }
    }

    resolve()
  })
}

module.exports = async () => {
  await stopMockServer()
}
