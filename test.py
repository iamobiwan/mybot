import subprocess

remote_sync_config = subprocess.run(
    ['ssh', '-o ConnectTimeout=1', '-o ConnectionAttempts=1',
    f'root@185.103.254.12',
    'cat /etc/wireguard/sync.conf'],
    capture_output=True, text=True)
remote_wg0_config = subprocess.run(
    ['ssh', '-o ConnectTimeout=1', '-o ConnectionAttempts=1',
    f'root@185.103.254.12',
    'cat /etc/wireguard/wg0.conf'],
    capture_output=True, text=True)
with open(f'servers/loki/sync.conf', 'r') as file:
    local_sync_config = file.read()
with open(f'servers/loki/wg0.conf', 'r') as file:
    local_wg0_config = file.read()
# print(remote_sync_config.stdout)
# print('---------')
# print(local_sync_config)
# print('---------')
# print(remote_wg0_config)
# print('---------')
# print(local_wg0_config)


if remote_sync_config.stdout == local_sync_config and remote_wg0_config.stdout == local_wg0_config:
    print('True')