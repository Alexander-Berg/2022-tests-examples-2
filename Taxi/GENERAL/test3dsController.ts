import {Request, Response} from 'express'

const MOCK_TEXT =
  'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad, adipisci consequuntur cum doloremque harum, incidunt laborum maiores modi natus omnis placeat possimus quidem sapiente sit temporibus vitae voluptate. Laboriosam, repellat.'

const CONTENT = Array(10)
  .fill(null)
  .map(() => MOCK_TEXT)

export const test3dsController = (_: Request, res: Response) => {
  return res.send(
    `<html> 
        <head><title>Test 3ds page title</title></head>
        <body>
            <h1>Test 3ds page</h1>
            <!-- TODO: сделать проверку на failed status yalavka-396 -->
            <p>Wait for success status...</p>
            <p>${CONTENT}</p>
        </body>
        <script>
            async function sendSuccess3dsMessage() {
                 await new Promise(resolve => setTimeout(resolve, 300))
                 window.top.postMessage(JSON.stringify({type: 'BEFORE_REDIRECT_BY_POST'}), '*')
                 /* даём паузу, чтобы точно успеть снять скриншот */
                 await new Promise(resolve => setTimeout(resolve, 800))
                 window.top.postMessage(JSON.stringify({type: '3DS_SUCCESS'}), '*')
            }
            sendSuccess3dsMessage()
        </script>
     </html>`,
  )
}
