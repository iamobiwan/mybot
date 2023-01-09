cp servers/$1/wg0.conf servers/backup/$1_$(date +%d%m%Y-%H:%M:%S)
sudo wg-quick strip server/$1/wg0.conf > servers/$1/sync.conf