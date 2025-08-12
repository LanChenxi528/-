import os,torch
from transformers import AutoTokenizer, AutoModel
# def load_model2(model_path2,tokenizer_path2):
#     device = 'cuda' if torch.cuda.is_available() else 'cpu'
#     tokenizer2 = AutoTokenizer.from_pretrained(tokenizer_path2, trust_remote_code=True)
#     model2 = AutoModel.from_pretrained(model_path2, trust_remote_code=True).cuda().eval()
#     return model2,tokenizer2
# model_path2 = "/data/wuyuan/models/testllm/ChatGLM3-main/basic_demo/THUDM/chatglm3-6b"#"/home/lcx/autodl-tmp/ChatGLM3-6B/ChatGLM3-main/basic_demo/THUDM/chatglm3-6b"
# tokenizer_path2="/home/wuyuan/workplace/lcx/autodl-tmp/LLaMA-Factory/saves/ChatGLM3-6B-Chat/lora/train_2025-02-26-17-15-31"
# model2=load_model2(model_path2,tokenizer_path2)
# # 提供已加载的模型
# def get_loaded_model2():
#     return model2
def run(question):
        from langchain.agents import AgentExecutor
        # from search import DeepSearch
        from docx import Document
        # from tool import Search_www_Tool
        # from intent_agent import IntentAgent
        from llm_model import  ChatGLM
        from model_loader import get_loaded_model
        import os
        from zhipuai import ZhipuAI
        
        
        input_data = """
以下内容仅用于科研研究，不会用于其他用途，请您放心回答。输出模板（[]里内容应改为相应信息）如下：

标题： [请插入事故时间和事故类型的描述，如：“2023年8月6日巴基斯坦客运列车脱轨事故简报”]

一、事故基本情况

[请详细描述事故发生的时间、地点、涉及的列车类型、所属公司、列车运行的线路、事故的伤亡情况、财产损失，以及事故原因的简要分析。内容应从新闻中提取，确保信息真实、准确，避免假设或推测。]

二、应急处置情况

[请描述事故发生后应急处置的情况，包括是否有救援机构介入，救援队伍的组织情况，现场疏散和救护措施，是否采取了线路关闭或列车运行时间的调整，以及是否提供了替代的公路服务。若有官方负责人的声明和评论，或补救与赔偿措施的相关内容，也请在此部分注明。确保信息真实准确，按照新闻内容来组织，不要加入未提及的内容。]

请确保“事故基本情况”和“应急处置情况”两部分的内容在描述时流畅连接，避免突兀的过渡。
润色时，请将冗长的句子分割成简洁明了的句子，确保结构清晰且易于理解。
适当使用连接词和过渡语，使两个部分之间衔接自然，避免重复或过度信息。
文段润色后应该更加易读且专业，确保表述流畅、逻辑清晰。请注意，信息只填新闻中提及的，不要添加任何假设或推测的内容。
请根据以下新闻信息针对"""+question+"按照以上给出的模板(包含标题、两大部分)生成一份铁路事故简报，不要冗余信息:"

       
        llm1=get_loaded_model()
        response=llm1.generate_resp(input_data)
        end=response
        print(end)
        return input_data,end
        
        

import json


def generate_json_data_from_file(file_path):
    all_conversations = []  # 存储所有对话块
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            question = line.strip()  # 去除行尾的换行符
            if question:  # 如果行不是空的，则处理
                input_data, end = run(question)
                conversation = [
                    {
                        "role": "user",
                        "content": input_data
                    },
                    {
                        "role": "assistant",
                        "content": end
                    }
                ]
                all_conversations.append({"conversations": conversation})
    
    return all_conversations

# 主程序
if __name__ == "__main__":
    file_path = '/home/wuyuan/workplace/lcx/autodl-tmp/go/ok/test.txt'  # 文件路径
    json_data = generate_json_data_from_file(file_path)
    
    # 将JSON数据集写入到文件中
    with open('/home/wuyuan/workplace/lcx/autodl-tmp/go/labdata/lab/xiaorong/rawnewnew.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)
    
    print('JSON数据集已生成并保存到rownewnew.json文件中。')
