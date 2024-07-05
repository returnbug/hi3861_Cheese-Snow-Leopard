from flask import *
from flask_cors import CORS
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)
CORS(app)


# 默认get请求
@app.route('/hello')
def hello_world():
    return 'Hello world'


@app.route('/post', methods=["post"])
def post():
    name = request.form.get("name")
    age = request.form.get("age")
    print(name + " " + age)
    return "OK"


@app.route('/getPCD/<pcd>')
def getPCD(pcd):
    return send_from_directory("pcds", f"{pcd}.pcd", as_attachment=True)


@app.route('/getData', methods=["get"])
def getData():
    engine = create_engine("mysql+pymysql://root:root@127.0.0.1:3306/iot?charset=utf8mb4")
    connection = engine.connect()
    try:
        sql_query = "SELECT * FROM pcds"
        result = connection.execute(text(sql_query))
        data = [dict(row._mapping) for row in result]  # 关键修正：使用row._mapping确保行数据正确转换为字典
        return jsonify(data)
    except Exception as e:
        error_message = str(e)
        print(f"Unexpected error: {error_message}")
        return jsonify({"error": error_message}), 500
    finally:
        connection.close()


@app.route('/getImage', methods=["get"])
def get_image_url():
    name = request.args.get('num')
    dict = []
    image_list = os.listdir('images')
    for image in image_list:
        img_name = image.split('_')[0]
        if img_name == str(name):
            img_url = 'http://127.0.0.1:80/download_image/images/'+image
            dict.append(img_url)
    return jsonify({"data": dict}), 200


@app.route('/download_image/images/<image>', methods=['get'])
def download_image(image):
    image_path = os.path.join('images', image)
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    else:
        return 'Image not found', 404


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 这里host是你的后端地址，这里写0.0.0.0， 表示的是这个接口在任何服务器上都可以被访问的到，只需要前端访问该服务器地址就可以的，
    # 当然你也可以写死，如222.222.222.222， 那么前端只能访问222.222.222.222, port是该接口的端口号,
    # debug = True ,表示的是，调试模式，每次修改代码后不用重新启动服务
    app.run(host='0.0.0.0', port=80, debug=True)
