from __future__ import print_function

import logging
import os
import paramiko
from scp import SCPClient
import sys
import time
import gphoto2 as gp


def main():
    x = 0
    while x < 5:
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
        print('Copying image to', target)
        camera_file = gp.check_result(gp.gp_camera_file_get(
                camera, file_path.folder, file_path.name,
                gp.GP_FILE_TYPE_NORMAL, context))
        gp.check_result(gp.gp_file_save(camera_file, target))
        gp.check_result(gp.gp_camera_exit(camera, context))
        # Send files to the server
        ssh = copy_to_server(server='192.168.8.111')
        scp = SCPClient(ssh.get_transport())
        scp.put(files=local_file_path, remote_path='/media/Kratos/Timelapse')
        # Remove file from the app's temp storage
        os.remove(local_file_path)
        x += 1
        time.sleep(5)


def copy_to_server(server='192.168.8.111', port=22, user='root', password='libreelec'):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

if __name__ == "__main__":
    sys.exit(main())
