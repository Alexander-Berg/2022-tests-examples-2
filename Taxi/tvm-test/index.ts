import axios from 'axios'
import {pickBy} from 'lodash-es'

export async function getTVMTicket(dst: string): Promise<string> {
  const config = {
    url: 'http://localhost:8002/tvm/tickets',
    params: pickBy({
      dsts: dst,
    }),
    timeout: 100,
  }
  let tvmError = null
  let retryAttempts = Number(process.env.EDA_WEB_TVM_RETRY_ATTEMPTS || 1)

  while (retryAttempts-- > 0) {
    try {
      const {data} = await axios({
        ...config,
        headers: {
          Authorization: 'tvmtool-development-access-token',
        },
      })

      return data[dst].ticket
    } catch (err) {
      console.log(`Ошибка при получении getTVMTicket. Config: ${JSON.stringify(config)}`)
      console.error(err)
      tvmError = err
    }
  }

  throw new Error(`TVM error: ${tvmError ? tvmError.toString() : ''}; params: ${JSON.stringify(config)}`)
}
