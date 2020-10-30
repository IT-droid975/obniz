import cv2
import io
import os
from google.protobuf.json_format import MessageToJson
#from google.protobuf import json_format
import json
from google.cloud import vision
from google.cloud.vision import types

import asyncio
import sys
from obniz import Obniz

import time
import remove_photo

try:
    async def onconnect(obniz):
        led = obniz.wired("LED",{"anode":0,"cathode":1})

        #今回の作業用ディレクトリ
        base_dir = r'ディレクトリ名'
        #さっきのJSONファイルのファイル名
        credential_path = base_dir + r'API_KEY.json'
        #サービスアカウントキーへのパスを通す
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
        #visionクライアントの初期化
        client = vision.ImageAnnotatorClient()

        i=0
        while True:
            # 2 回撮影
            #時間経過はまた今度
            if(i==2):
                print("end")
                time.sleep(3)
                break

            #ledがおっつかない
            if(i>1):
                time.sleep(3)

            fileName = "photo_"+ str(i) +".png"
            # 内蔵カメラのデバイスIDは0、USBで接続したカメラは1以降。
            capture = cv2.VideoCapture(0)
            # 取得した画像データは変数imageに格納。retは取得成功変数。
            ret, image = capture.read()
            if ret == True:
                # 取得した画像を出力。fileNameは出力する画像名。
                cv2.imwrite("./photo/"+fileName, image)
            #対象となる画像のファイル名
            file_name = base_dir + "photo/"+fileName
            with io.open(file_name, 'rb') as image_file:
                content = image_file.read()
            image = types.Image(content=content)
            objects = client.object_localization(
                image=image).localized_object_annotations
            #print('Number of objects found: {}'.format(len(objects)))

            p=0
            for object_ in objects:
                #↓一覧表示
                # print('\n{} (confidence: {})'.format(object_.name, object_.score))
                #合致率60%以上でカウント
                if object_.name == "Person" :
                    if object_.score > 0.60 :
                        p = p+1
                # print('Normalized bounding polygon vertices: ')
                # for vertex in object_.bounding_poly.normalized_vertices:
                #     print(' - ({}, {})'.format(vertex.x, vertex.y))
            print(str(p)+"名")
            if(p > 0):
                ##obnizでやりたい処理
                for l in range(0,1):
                    led.on()
                    obniz.wait(500)
                    led.off()
                    break
                ##↑↑obnizでやりたい処理
            #visionクライアントの初期化
            client = vision.ImageAnnotatorClient()
            i=i+1
        #↓別プログラム(写真を削除する用)
        remove_photo.remove_photo()
        #obnizのクリーンアップ？
        obniz.close()

    #obnizの接続
    obniz = Obniz('9260-1198')
    #obniz.debugprint = True
    obniz.onconnect = onconnect
    asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    #ctrl+c
    obniz.close()
    print("finish")
