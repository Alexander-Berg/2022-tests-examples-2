yav:
  files:
    /etc/odyssey/ssl/server.pem:
      owner: 'postgres:postgres'
      mode: '0440'
      secret: 'sec-01dz6ecgksesbgpa5xmtg8qpvk'
      key: 'cert.pem'
    /etc/pgbouncer/ssl/client.pem:
      owner: 'postgres:postgres'
      mode: '0440'
      secret: 'sec-01dz6ecgksesbgpa5xmtg8qpvk'
      key: 'cert.pem'
