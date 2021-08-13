# 智慧生活-家庭監控系統
## 製作動機
最近從Tibame結訓後，想要找一份作品來實作充實自己，也剛好朋友在中央大學進修在職專班，課堂上有使用樹梅派實作iot的相關作業，就與他一起討論及實作了這份作品

## 專案說明
為了達到居住安全，避免外出時家裡遭陌生人闖入，大部分家庭可能會在家門口安裝監視器，但是並沒有辦法無時無刻去注意監視器的畫面，如果要安裝保全，對於小家庭來說成本又會太高，所以我這裡實作了一個家庭監控系統安裝在在家門口，若有人靠近家門時，會開啟攝像頭進行拍照，並將照片第一時間傳給使用者，以便提前防範。

## 技術說明
- 使用樹梅派(Raspberry Pi 4 Model B)加上紅外線感測器及攝像頭進行家庭監控，並建立LineBot作為通知使用者的App

### 感應器連接
- 紅外線感應器是使用GPIO與樹梅派進行連接，將感應器GPIO的三個接頭由左至右(白、灰、黑)分別連接至樹梅派的(5V、Board Pin11(GPIO17)、Ground)
![S__168542210](https://user-images.githubusercontent.com/78791996/128961926-32ad7927-e507-4523-a27f-66b967208dbe.jpg)
![擷取](https://user-images.githubusercontent.com/78791996/128961933-1d8e97a7-e882-4350-bbbd-aea347638cc3.PNG)

- 最後透過pyhton程式碼實作`main.py`

### 物件偵測

#### 攝像頭安裝及設定
- 攝像頭的部分我使用Rasberry Pi camera Rev 1.3(2592 × 1944 pixels)
![S__168689669](https://user-images.githubusercontent.com/78791996/129122858-6355a788-2c51-4d95-a091-6c4ab7eeca7c.jpg)
- 安裝步驟如下:
  1. 先將樹梅派關機
  ```bash 
  sudo shutdown –h now
  ``` 
  2. 連接攝像頭
  ![S__168689670](https://user-images.githubusercontent.com/78791996/129126215-477a697d-8961-4c9d-af1d-fecaa99fe469.jpg)
  ```bash
  sudo raspi-config  # 設定攝像頭
  
  # Interface Options -> Camera -> enable -> yes 
  ``` 
  3. 重新啟動樹梅派
  ```bash 
  sudo reboot
  ```  
  4. 測試是否可以進行拍照
  ```bash 
  raspistill -o test.jpg
  ``` 
以上基礎設定完成後，接下來安裝相關套件

#### 套件安裝
- 我們需要用到opencv、tensorflow...等套件，故我們會在樹梅派系統預先安裝相關的Packages
```bash
# Get packages required for OpenCV

sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get -y install libxvidcore-dev libx264-dev
sudo apt-get -y install qt4-dev-tools libatlas-base-dev
```
-  安裝`requirements.txt`檔案內的相關套件
```bash
sudo pip3 install -r requirements.txt
```
- 預設安裝的tensorflow會出現下圖所顯示的錯誤，我們需重新安裝某些特定版本的Packages
![image](https://user-images.githubusercontent.com/78791996/129132603-5b1e6eb8-974a-4d5b-a5f6-c0b2bf3104b1.png)
```bash
# Fix problem

sudo apt-get install -y libhdf5-dev libc-ares-dev libeigen3-dev
python3 -m pip install keras_applications==1.0.8 --no-deps
python3 -m pip install keras_preprocessing==1.1.0 --no-deps
python3 -m pip install h5py==2.9.0
sudo apt-get install -y openmpi-bin libopenmpi-dev
sudo apt-get install -y libatlas-base-dev
python3 -m pip install -U six wheel mock
wget https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.0.0/tensorflow-2.0.0-cp37-none-linux_armv7l.whl
python3 -m pip uninstall tensorflow
python3 -m pip install tensorflow-2.0.0-cp37-none-linux_armv7l.whl
```
- 下載並使用Tensorflow Lite已經pre-train好的Model做為物件辨認
```bash
wget https://storage.googleapis.com/ download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_ 06_29.zip -d Sample_TFLite_model
```
- 為了加快Tensorflow Lite的執行速度，我們使用`tflite_runtime`的Package
```bash
sudo pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl
```
參考網站:https://www.tensorflow.org/lite/guide/python




### 傳送訊息
若物件偵測為人的情況，則會透過Line-bot將訊息傳送給使用者

### 自動化執行程式



