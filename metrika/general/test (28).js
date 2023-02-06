import fs from 'fs'

/**
 * Here you can test everything else
 */

export default [{
  method: 'get',
  route: [
    '/soundwave/',
    '/soundwave/:ssid',
  ],
  controller: (req, res) => {
    let html = fs.readFileSync(`${SERVER_ROOT}/static/soundwave.html`).toString()
    html = html.replace('<!-- PARAMS -->', `<script>window.PARAMS = ${JSON.stringify(req.params)}</script>`)
    res.status(200).send(html)
  }
}]
