import requests
from transformers import AutoTokenizer, AutoModel
from flask import Flask, request, jsonify, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from zhipuai import ZhipuAI
from GLM3_agent import GLM3_agent
import re
import threading
# import zhipuai
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app, resources={r"/*": {"origins": "*"}})


# ... 路由和处理函数 ...
@app.route('/hello')
def hello():
    return 'hello'
from docgenerate import Doc_Generate
def generate_word(unique_id, answer):
    Doc_Generate(unique_id, answer)
    print("注意！此时word文档已分割完毕！\n")
from docsmallgenerate import Doc_SmallGenerate
def small_generate_word(unique_id, answer):
    Doc_SmallGenerate(unique_id, answer)
    print("注意！此时word文档已分割完毕！\n")
@app.route('/chat', methods=['POST'])
def chat():
    try:
        print("ok")
        messages = request.json["messages"]
        content = messages[-1]["content"]
        print(content)
        # 调用生成函数
        answer = GLM3_agent.run(content, "../../../chatglm3")#path没用上，缺省即可
        #31行到70行为模块2处理办法       if answer=="对于日期不明确的输入类型，模块功能尚未完善，请下次再来，谢谢":
        if "一、事故概况："in answer:
            from docsmallgenerate import Doc_SmallGenerate
            import uuid  # 导入uuid模块
            unique_id1 = str(uuid.uuid4())
            word_thread0 = threading.Thread(target=small_generate_word, args=(unique_id1, answer))
            word_thread0.start()
            # Doc_SmallGenerate(unique_id1,answer)
            parts = re.split('标题：|一、事故概况：|参考站源：', answer)
            title = parts[1].strip().replace('标题：', '')
            related_list = parts[2].strip().replace('：', '')
            accident_dates = re.findall(r'\d{4}年\d{1,2}月\d{1,2}日', related_list)
            print("请注意，现在输出的是模块二提取出来的时间列表\n")
            print(accident_dates)
            related_events = []
            for i, date in enumerate(accident_dates):
                # start_index = related_list.find(date)
                if i==0:start_index = related_list.find(date)
                if i < len(accident_dates) - 1:
                    next_date_index = related_list.find(accident_dates[i + 1],start_index + 1)
                    if next_date_index != -1:
                        end_index = next_date_index
                    else:
                        end_index = len(related_list)
                else:
                    end_index = len(related_list)
                event = related_list[start_index:end_index].strip()
                start_index=end_index
                print("请注意，现在输出的是模块二提取出来的每一条数据\n")
                print(event)
                related_events.append(event)
            references = parts[3].strip()
            references_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', references)
            responsetest1 = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "id": unique_id1,
                        "title":title,
                        "related_list":related_events,
                        "references_urls":references_urls
                    }
                }
            ],
            "code":200
        }
            return jsonify(responsetest1)
        
        if answer=="请按提示输入规范的检索词。如若生成某具体事故的简报，请输入“X年X月X日X地X事故”；如若查询某年/某地/某类事故，请输入“X年X事故/X地X事故”":
            responsetest2 = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": answer
                    }
                }
            ],
            "code":400
        }
            return jsonify(responsetest2)
        if answer=="没有查询到相关内容。":
            answer="没有查询到相关内容，请您仔细检查您的提问内容，进行调整后重试。"
            responsetest3 = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": answer
                    }
                }
            ],
            "code":400
        }
            return jsonify(responsetest3)
        
        # import threading
        from docgenerate import Doc_Generate
        import uuid  # 导入uuid模块
        # 生成唯一标识符
        unique_id = str(uuid.uuid4())
        word_thread = threading.Thread(target=generate_word, args=(unique_id, answer))
        word_thread.start()
        # Doc_Generate(unique_id,answer)
        print("注意！此时word文档已分割完毕！\n接下来该对返回到前端的数据进行处理了\n")

        # 、使用正则表达式分割文本
        parts = re.split('一、事故基本情况|二、应急处置情况|三、相关事故列表|参考站源：', answer)
        # 标题
        # title = parts[0].strip().replace('标题:','')
        title = parts[0].strip().replace('标题：','')
        print("模块1的终端数据返回标题是："+title)

        # 事故基本情况
        accident_info = parts[1].strip()
        # 应急处置情况
        emergency_response = parts[2].strip()
        # 相关事故列表
        related_list = parts[3].strip()
        # 从相关事故列表总字符串中提取日期和事件
        accident_dates = re.findall(r'\d{4}年\d{1,2}月\d{1,2}日', related_list)
        # 创建一个空列表来存储事件
        related_events = []
        for i, date in enumerate(accident_dates):
            # 查找日期在相关事故列表中的索引位置
            start_index = related_list.find(date)
            # 找到下一个日期的索引位置
            if i < len(accident_dates) - 1:
                next_date_index = related_list.find(accident_dates[i + 1], start_index + 1)
                # 如果找到下一个日期，则以其索引位置作为事件的结束位置
                if next_date_index != -1:
                    end_index = next_date_index
                else:
                    # 如果找不到下一个日期，则以相关事故列表的末尾作为事件的结束位置
                    end_index = len(related_list)
            else:
                # 如果当前日期是最后一个日期，则以相关事故列表的末尾作为事件的结束位置
                end_index = len(related_list)
            event = related_list[start_index:end_index].strip()
            related_events.append(event)#所有相关事故存入list
        print("模块1的终端数据返回事故列表是：\n")
        print(related_events)
        print()
        # 参考站源
        references = parts[4].strip()
        # references中保存了若干个http开头的网站链接
        # 使用正则表达式匹配网站链接
        references_urls = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', references)
        response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "id": unique_id,
                        # "content": answer
                        "title": title,
                        "accident_info": accident_info,
                        "emergency_response": emergency_response,
                        "related_list": related_events,
                        "references_urls": references_urls
                    }
                }
            ],
            "code":200
        }
        return jsonify(response)

    except Exception as e:
        print('Error:', str(e))
        # return jsonify({'error': 'Error fetching response'})
        responsetest4 = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "网络波动，请稍后再试"
                    }
                }
            ],
            "code":400
        }
        return jsonify(responsetest4)

from flask import request, jsonify,send_file
import os
@app.route('/download', methods=['POST'])
def download():
    try:
        if request.method == 'POST':
            # 获取 JSON 数据
            data = request.json
            if data and 'file_id' in data:
                # 从 JSON 数据中获取文件 ID
                file_id = data['file_id']
                # 构建文件路径
                file_path = f"word_save/{file_id}.docx"
                # 检查文件是否存在
                if os.path.exists(file_path):
                    # 发送文件到前端
                    return send_file(file_path, as_attachment=True)
                else:
                    return "File not found", 404  # 如果文件不存在，则返回404错误
            else:
                return "Invalid JSON data", 400  # 如果JSON数据无效，则返回400错误
        else:
            return "Method not allowed", 405  # 如果请求方法不是POST，则返回405错误
    except Exception as e:
        return str(e), 500  # 如果发生异常，则返回500错误

if __name__ == '__main__':
    with app.app_context():
        socketio.run(app, host='0.0.0.0', port=6135, debug=False, allow_unsafe_werkzeug=True)