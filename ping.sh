while true; do
  echo $(curl -s http://localhost:8080/count/1)
  sleep 2
done