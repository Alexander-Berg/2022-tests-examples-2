yav:
  files:
    /etc/odyssey/ssl/server.pem:
      owner: 'postgres:postgres'
      mode: '0440'
      secret: 'sec-01dz6efeydr99zx2wcqkbnepbw'
      key: 'cert.pem'
    /etc/pgbouncer/ssl/client.pem:
      owner: 'postgres:postgres'
      mode: '0440'
      secret: 'sec-01dz6efeydr99zx2wcqkbnepbw'
      key: 'cert.pem'
