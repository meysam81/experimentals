client=$(hydra create oauth2-client -e http://localhost:41100 --name demo --grant-type authorization_code,refresh_token,client_credentials,implicit --scope openid,offline --redirect-uri http://localhost:41200/ --format json --response-type code,token,id_token)

client_id=$(echo $client | jq -r '.client_id')
client_secret=$(echo $client | jq -r '.client_secret')
