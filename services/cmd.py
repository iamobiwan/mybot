import subprocess

cmd = [
    'rsync',
    '-avz',
    '/home/crash/projects/endurance-vpn-bot/servers/config/',
    'root@185.103.254.12:/etc/wireguard/'
    ]

p = subprocess.run(
    cmd,
    capture_output=True,
    text=True
)
print(p.stdout)
print('sending' in p.stdout.split())
# for i in p.stdout:
#     print(f'!! {i}')
