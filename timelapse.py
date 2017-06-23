from __future__ import print_function
import argparse
import logging
import os
import paramiko
from scp import SCPClient
import sys
import time
import gphoto2 as gp


def main():
    parser = argparse.ArgumentParser(description='Timelapse app')
    parser.add_argument('-n', '--num_of_shots', help='Number of shots to take', required=False)
    parser.add_argument('-t', '--sleep_time', help='Time between shots', required=False)
    parser.add_argument('-s', '--send_to_server', help='Whether use the server. Y or N', required=False)
    args = vars(parser.parse_args())
    if args['num_of_shots']:
        num_of_shots = args['num_of_shots']
        print('The number of shots is: ' + str(num_of_shots))
    else:
        num_of_shots = 10
    if args['sleep_time']:
        sleep_time = args['sleep_time']
        print('The sleep time is: ' + str(sleep_time))
    else:
        sleep_time = 5
        print('The sleep time is: ' + str(sleep_time))
    if args['send_to_server']:
        send_to_server = args['send_to_server']
        if send_to_server == 'y':
            print('The files will be sent to the server')
        else:
            print('The files will not be sent to the server')
    else:
        send_to_server = 'n'
        print('The files will not be sent to the server')
    x = 1
    while x < num_of_shots:
        logging.basicConfig(
            format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
        gp.check_result(gp.use_python_logging())
        context = gp.gp_context_new()
        camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(camera, context))
        print('Capturing image')
        file_path = gp.check_result(gp.gp_camera_capture(
            camera, gp.GP_CAPTURE_IMAGE, context))
        print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
        local_pics_directory = 'pics'
        if not os.path.exists(os.path.join(os.getcwd(), local_pics_directory)):
            os.makedirs(local_pics_directory)
        local_file_path = 'pics/' + file_path.name
        target = os.path.join(os.getcwd(), local_file_path)
        print('Attempt number ' + str(x))
        print('Copying image to', target)
        camera_file = gp.check_result(gp.gp_camera_file_get(
                camera, file_path.folder, file_path.name,
                gp.GP_FILE_TYPE_NORMAL, context))
        gp.check_result(gp.gp_file_save(camera_file, target))
        gp.check_result(gp.gp_camera_exit(camera, context))
        # Send files to the server
        if send_to_server == 'y':
            try:
                ssh = copy_to_server(server='192.168.8.111')
                print('Copying image to the server')
                scp = SCPClient(ssh.get_transport())
                scp.put(files=local_file_path, remote_path='/media/Kratos/Timelapse')
                os.remove(local_file_path)
            except:
                print('server not connected')
                pass
        else:
            print('Files are not being sent to the server')
            # Remove file from the app's temp torage
        x += 1
        time.sleep(float(sleep_time))


def copy_to_server(server='192.168.8.111', port=22, user='root', password='libreelec'):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

if __name__ == "__main__":
    sys.exit(main())
