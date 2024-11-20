import os
import time
import PySpin
import sys
import socket
import numpy as np
from datetime import date, timedelta
import datetime


class CameraController:
    def __init__(self):
        # Camera settings
        self.imgsMax = 120000  # Maximum number of images to save
        self.dayIndex = 0

        # Auto-adapt parameters
        self.auto_adapt_parameters = {
            'exposureTime': 11,
            'exposureMax': 1024,
            'exposure_step': 5,
            'gainNum': 0,
            'gainMax': 10,
            'gain_step': 2,
            'img_mean_min': 120,
            'img_mean_max': 170,
        }

        # Transmission settings
        self.Need_transmition = True
        self.HOST = '10.92.201.113'
        self.PORT = 11111

        # Other settings
        self.Auto_adapt = True
        self.sleepTime = 6

        # Path setup
        self.setup_paths()

    def setup_paths(self):
        self.filePath = '/home/oceanthink/Documents/'
        self.dir_pre = self.filePath + 'imgs/'
        self.logPath = self.filePath + 'logs/'

        os.makedirs(self.dir_pre, exist_ok=True)
        os.makedirs(self.logPath, exist_ok=True)

        folder_name = 'station_'
        numList = []
        for file in os.listdir(self.dir_pre):
            if os.path.isdir(os.path.join(self.dir_pre, file)):
                if folder_name in file:
                    numList.append(int(file.split('_')[1]))

        if len(numList) == 0:
            self.folder_name = os.path.join(self.dir_pre, folder_name + str(0))
        else:
            self.folder_name = os.path.join(self.dir_pre, folder_name + str(max(numList) + 1))

        self.imgPath = f"{self.folder_name}_{self.dayIndex}"
        os.makedirs(self.imgPath, exist_ok=True)

        local_time = time.strftime("%Y%m%d_%H%M%S")
        self.logFile = f"{self.logPath}log_{local_time}.txt"

    def setExposure(self, cam, exposure_time):
        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time)
        exposure_time_to_set = max(cam.ExposureTime.GetMin(), exposure_time_to_set)
        cam.ExposureTime.SetValue(exposure_time_to_set)
        print('Exposure is set to', exposure_time_to_set)

    def setGain(self, cam, gain):
        gain_to_set = min(cam.Gain.GetMax(), gain)
        gain_to_set = max(cam.Gain.GetMin(), gain_to_set, 0)
        cam.Gain.SetValue(gain_to_set)
        print('Gain is set to', gain_to_set)

    def send_one_img(self, img_path, timeout=30):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((self.HOST, self.PORT))

                file_name = os.path.basename(img_path).encode()
                name_length = len(file_name)
                s.sendall(name_length.to_bytes(4, byteorder='big'))
                s.sendall(file_name)

                file_size = os.path.getsize(img_path)
                s.sendall(file_size.to_bytes(8, byteorder='big'))

                with open(img_path, 'rb') as file:
                    while True:
                        data = file.read(8192)
                        if not data:
                            break
                        s.sendall(data)

                confirmation = s.recv(2)
                if confirmation == b'OK':
                    print(f"Image '{img_path}' sent successfully")
                    return True
                else:
                    print("Failed to get confirmation from server")
                    return False

        except Exception as e:
            print(f"Error sending {img_path}: {e}")
            return False

    def set2NewestMode(self, cam):
        s_node_map = cam.GetTLStreamNodeMap()

        handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
        if not PySpin.IsReadable(handling_mode) or not PySpin.IsWritable(handling_mode):
            print('Unable to set Buffer Handling mode (node retrieval). Aborting...\n')
            return False

        stream_buffer_count_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferCountMode'))
        stream_buffer_count_mode_manual = PySpin.CEnumEntryPtr(stream_buffer_count_mode.GetEntryByName('Manual'))
        stream_buffer_count_mode.SetIntValue(stream_buffer_count_mode_manual.GetValue())

        buffer_count = PySpin.CIntegerPtr(s_node_map.GetNode('StreamBufferCountManual'))
        buffer_count.SetValue(1)  # Set to 1 buffer for newest only mode

        handling_mode_entry = handling_mode.GetEntryByName('NewestOnly')
        handling_mode.SetIntValue(handling_mode_entry.GetValue())
        print('Buffer Handling Mode set to NewestOnly')

    def acquire_images(self, cam, nodemap):
        try:
            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            cam.GainAuto.SetValue(PySpin.GainAuto_Off)
            cam.Gain.SetValue(self.auto_adapt_parameters['gainNum'])
            cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            cam.ExposureTime.SetValue(self.auto_adapt_parameters['exposureTime'])

            self.set2NewestMode(cam)
            cam.BeginAcquisition()

            processor = PySpin.ImageProcessor()
            processor.SetColorProcessing(PySpin.HQ_LINEAR)

            imgList = os.listdir(self.imgPath)
            imgList.sort()
            imgIndex = int(imgList[-1].split('Cap_')[-1].split('.')[0]) + 1 if imgList else 1

            now = datetime.datetime.now()
            next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

            while True:
                self.process_single_image(cam, processor, imgIndex, next_midnight)
                imgIndex = (imgIndex % self.imgsMax) + 1

                now = datetime.datetime.now()
                if now >= next_midnight:
                    self.dayIndex += 1
                    next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    self.imgPath = f"{self.folder_name}_{self.dayIndex}"
                    os.makedirs(self.imgPath, exist_ok=True)

        except Exception as ex:
            print(f'Error: {ex}')
            with open(self.logFile, 'a') as f:
                f.write(f'Error: {ex}\n')
        finally:
            cam.EndAcquisition()

    def process_single_image(self, cam, processor, imgIndex, next_midnight):
        try:
            image_result = cam.GetNextImage(1000)
            if image_result.IsIncomplete():
                with open(self.logFile, 'a') as f:
                    f.write(f'Image incomplete with status {image_result.GetImageStatus()}\n')
                return

            image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
            need_save = self.adjust_image_parameters(cam, image_converted)

            if need_save:
                self.save_and_transmit_image(image_converted, imgIndex)
                time.sleep(self.sleepTime)

            image_result.Release()

        except PySpin.SpinnakerException as ex:
            print(f'Error: {ex}')
            with open(self.logFile, 'a') as f:
                f.write(f'Error: {ex}\n')

    def adjust_image_parameters(self, cam, image_converted):
        if not self.Auto_adapt:
            return True

        image_array = image_converted.GetNDArray()
        image_mean = np.mean(image_array)
        print(f'Current image mean brightness: {image_mean}')

        if image_mean < self.auto_adapt_parameters['img_mean_min']:
            return self.handle_low_brightness(cam, image_mean)
        elif image_mean > self.auto_adapt_parameters['img_mean_max']:
            return self.handle_high_brightness(cam, image_mean)
        else:
            print('Brightness in normal range, saving image')
            return True

    def handle_low_brightness(self, cam, image_mean):
        if self.auto_adapt_parameters['exposureTime'] < self.auto_adapt_parameters['exposureMax']:
            self.auto_adapt_parameters['exposureTime'] += self.auto_adapt_parameters['exposure_step']
            self.setExposure(cam, self.auto_adapt_parameters['exposureTime'])
            return False
        elif self.auto_adapt_parameters['gainNum'] < self.auto_adapt_parameters['gainMax']:
            self.auto_adapt_parameters['gainNum'] += self.auto_adapt_parameters['gain_step']
            self.setGain(cam, self.auto_adapt_parameters['gainNum'])
            return False
        else:
            print('Maximum gain reached, image may be too dark')
            return True

    def handle_high_brightness(self, cam, image_mean):
        if self.auto_adapt_parameters['gainNum'] > 0:
            self.auto_adapt_parameters['gainNum'] -= self.auto_adapt_parameters['gain_step']
            self.setGain(cam, self.auto_adapt_parameters['gainNum'])
        elif self.auto_adapt_parameters['exposureTime'] > 0:
            self.auto_adapt_parameters['exposureTime'] -= self.auto_adapt_parameters['exposure_step']
            self.setExposure(cam, self.auto_adapt_parameters['exposureTime'])
        return False

    def save_and_transmit_image(self, image_converted, imgIndex):
        now = datetime.datetime.now()
        fileName = os.path.join(
            self.imgPath,
            f"{now.strftime('%H-%M-%S')}_{self.auto_adapt_parameters['gainNum']}_{self.auto_adapt_parameters['exposureTime']}.png"
        )
        print(f'Saving image as: {fileName}')
        image_converted.Save(fileName)

        if self.Need_transmition:
            try:
                self.send_one_img(fileName)
            except Exception as e:
                print(f'Transmission error: {e}')

    def run_single_camera(self, cam):
        try:
            cam.Init()
            nodemap = cam.GetNodeMap()
            self.acquire_images(cam, nodemap)
        except PySpin.SpinnakerException as ex:
            with open(self.logFile, 'a') as f:
                f.write(f'Error: {ex}\n')
        finally:
            cam.DeInit()

    def run(self):
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()

        try:
            for cam in cam_list:
                self.run_single_camera(cam)
        except Exception as e:
            print(e)
            with open(self.logFile, 'a') as f:
                f.write(f'{e}\n')
        finally:
            cam_list.Clear()
            system.ReleaseInstance()


def main():
    controller = CameraController()
    controller.run()


if __name__ == '__main__':
    main()