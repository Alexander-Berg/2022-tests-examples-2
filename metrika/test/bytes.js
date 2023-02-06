const bytesToSize = function (bytes) {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  if (bytes === 0) return '0 Byte'
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)), 10)
  return `${Math.round(bytes / Math.pow(1024, i), 2)} ${sizes[i]}`
}

const numberToBuffer = function () {
  let bytes = 0

  for (let i = 0; i < 100000; i++) {
    bytes += Buffer.from(`${i}`).length
  }

  console.log(bytesToSize(bytes * 1500000))
}

const string32ToBuffer = function () {
  let bytes = 0

  for (let i = 0; i < 100000; i++) {
    bytes += Buffer.from(i.toString(32)).length
  }

  console.log(bytesToSize(bytes * 1500000))
}

const string16ToBuffer = function () {
  let bytes = 0

  for (let i = 0; i < 100000; i++) {
    bytes += Buffer.from(i.toString(16)).length
  }

  console.log(bytesToSize(bytes * 1500000))
}

const string64ToBuffer = function () {
  let bytes = 0

  for (let i = 0; i < 100000; i++) {
    bytes += Buffer.from(i.toString(36)).length
  }

  console.log(bytesToSize(bytes * 1500000))
}

numberToBuffer()
string16ToBuffer()
string32ToBuffer()
string64ToBuffer()
