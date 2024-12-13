from flask import Flask
from flask import request
from flask import jsonify
import requests
import json
from PIL import Image
from pyzbar.pyzbar import decode
from werkzeug.serving import WSGIRequestHandler
import json
WSGIRequestHandler.protocol_version = "HTTP/1.1"

app = Flask(__name__)

#기본 url(제품명 받을 수 있는 url)
base_url = "http://openapi.foodsafetykorea.go.kr/api/0440dadbbd2047b8acc2/C005/json/1/5"

@app.route("/scan", methods=['POST'])
def scan_barcode():    
    #파일 필드 없거나 form-data 형식이 아닌 경우
    if 'file' not in request.files:
        return jsonify({'error':'No file'}),400

    file=request.files['file']

    #client 파일 선택 안했을 때
    if file.filename == '':
        return jsonify({'error' : 'No selected file'}), 400

    #이미지에서 바코드 번호 얻기
    try:
        image = Image.open(file)
        decoded = decode(image)

        #바코드의 번호 가져오기
        barcode_data = decoded[0].data.decode('utf-8')
        print(barcode_data)
       
        #url 완성해서 response 보내기
        api_url = f"{base_url}/BAR_CD={barcode_data}"
        response= requests.get(api_url)
        
        #정상 응답 확인
        if response.status_code == 200:            
                #json 파싱
                parsed = response.json()
                #코드 확인
                count = parsed["C005"]["total_count"]

                #에러 발생해서 중단될 경우
                if count == 0:
                    return jsonify({'error':'no item'}), 400
                else:
                    product_name=parsed["C005"]["row"][0]["PRDLST_NM"]
                    expiration_date = parsed["C005"]["row"][0]["POG_DAYCNT"]
                    return jsonify({'product_name':product_name, 'expiration_date':expiration_date}) ,200
        else:
                       
            return jsonify('error', 'no prodcut')

    except Exception as e:
        return jsonify({'error':str(e)}), 500

    
if __name__ == "__main__":
    app.run(host='localhost', port=8888)