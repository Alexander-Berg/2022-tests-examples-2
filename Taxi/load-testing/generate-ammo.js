require('dotenv').config()

const { createReadStream, createWriteStream, promises: fs } = require('fs')
const { createInterface } = require('readline')
const { once } = require('events')
const { execSync } = require('child_process')
const { join: joinPath } = require('path')
const os = require('os')
const config = require(joinPath(process.cwd(), '.load-testing', 'config.js'))

const [source, dest] = process.argv.slice(-2)

const HEADERS = [
  'Host: grocery-frontend-standalone.lavka.tst.yandex.net',
  'User-Agent: YaTank',
  'Connection: keep-alive',
]

const LUNAPARK_API_URL = 'https://lunapark.yandex-team.ru/api'

// Максимальное количество патронов
const MAX_AMMO = process.env.MAX_AMMO ? Number.parseInt(process.env.MAX_AMMO) : Number.MAX_SAFE_INTEGER

// Максимальное количество повторов одного и того же запроса (`0` — без ограничений)
const MAX_LOOP = process.env.MAX_LOOP ? Number.parseInt(process.env.MAX_LOOP) : 0

let REDUCTION_FACTOR = undefined

handle().catch((e) => console.error(e))

let destIx = 0

async function handle() {
  await fs.writeFile(dest, '')

  const destStream = createWriteStream(dest, { encoding: 'utf8' })

  destStream.once('finish', () => console.log(`Generated ammo total: ${destIx > 0 ? destIx - 1 : 0}`))

  const sourceStream = createReadStream(source, { encoding: 'utf8' })

  const rl = createInterface({
    input: sourceStream,
    crlfDelay: Infinity,
  })

  rl.on('line', (line) => {
    const ammo = getAmmo(line)

    if (ammo) {
      destIx++
      destStream.write(ammo)
    }
  })

  await once(rl, 'close')
  destStream.end()

  uploadAmmoFile()
}

function getAmmo(line) {
  if (destIx > MAX_AMMO) {
    return
  }

  try {
    const { cnt, method, request } = JSON.parse(line)

    if (request.includes('://')) {
      return
    }

    let ammo = `${method} ${request} HTTP/1.1\r\n` + HEADERS.join('\r\n') + '\r\n' + '\r\n'
    ammo = `${ammo.length} ${getTag(request)}` + '\r\n' + ammo

    return Array(handleCount(cnt)).fill(ammo).join('')
  } catch (e) {
    console.error(e)
  }
}

function handleCount(origCnt) {
  if (!MAX_LOOP) {
    return origCnt
  }

  if (REDUCTION_FACTOR === undefined) {
    REDUCTION_FACTOR = origCnt / MAX_LOOP
  }

  return Math.ceil(origCnt / REDUCTION_FACTOR)
}

function getTag(request) {
  if (request === '/' || startsWith(request, '/?')) {
    return 'index'
  }

  if (startsWith(request, '/category-group')) {
    return 'category'
  }

  if (startsWith(request, '/mobile')) {
    return 'mobile'
  }

  if (startsWith(request, '/goods')) {
    return 'goods'
  }

  if (startsWith(request, '/api/v1')) {
    return 'api_v1'
  }

  if (startsWith(request, '/api/v2')) {
    return 'api_v2'
  }

  if (startsWith(request, '/checkout')) {
    return 'checkout'
  }

  return 'unknown'
}

function startsWith(str, part) {
  return part === str.substr(0, part.length)
}

function uploadAmmoFile() {
  console.log('Uploading the ammo file...')

  const curl = [
    'curl',
    `${LUNAPARK_API_URL}/addammo.json`,
    `-F"login=${os.userInfo().username}"`,
    `-F"dsc=${config.recordingName}"`,
    `-F"file=@${dest}"`,
  ].join(' ')

  const result = execSync(curl)

  console.log(`Done: ${result}`)
  console.log('Update the "loadTesting.configData.ammofile" property in the "service.yaml" file')
}
