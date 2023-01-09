import psycopg2
from paramiko import SSHClient, AutoAddPolicy

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.load_system_host_keys()
client.connect(hostname='194.85.175.225', username='root')

# stdin, stdout, stderr = client.exec_command('cat /etc/wireguard/wg0.conf')

# print(stdout.read().decode('utf8'))
# print(stdout.channel.recv_exit_status())
# print(stdout.read().decode('utf8'))
try:
    sftp = client.open_sftp()
finally:
    remote_file = sftp.open('/etc/wireguard/test.conf')
    text = remote_file.read()
    print(text)
    remote_file.close()

# import subprocess

# command = ['sh', './test.sh', 'test']
# result = subprocess.run(command, capture_output=True, text=True)
# print(result.returncode, result.stdout, result.stderr)