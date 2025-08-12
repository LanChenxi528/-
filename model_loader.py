from llm_model import ChatGLM
def load_model(model_path):
    model = ChatGLM(model_path=model_path)
    model.load_model()
    return model
model_path = "/data/wuyuan/models/testllm/ChatGLM3-main/basic_demo/THUDM/chatglm3-6b"#"/home/lcx/autodl-tmp/ChatGLM3-6B/ChatGLM3-main/basic_demo/THUDM/chatglm3-6b"
loaded_model = load_model(model_path)
# 提供已加载的模型
def get_loaded_model():
    return loaded_model



from llm_model2 import ChatGLM2
model_path2 = "/data/wuyuan/models/testllm/ChatGLM3-main/basic_demo/THUDM/chatglm3-6b"#"/home/lcx/autodl-tmp/ChatGLM3-6B/ChatGLM3-main/basic_demo/THUDM/chatglm3-6b"
tokenizer_path2="/home/wuyuan/workplace/lcx/autodl-tmp/LLaMA-Factory/saves/ChatGLM3-6B-Chat/lora/train_2025-02-26-17-15-31"
def load_model2(model_path2,tokenizer_path2):
    model2 = ChatGLM2(model_path=model_path2,tokenizer_path=tokenizer_path2)
    model2.load_model()
    return model2
model2=load_model2(model_path2,tokenizer_path2)
# 提供已加载的模型
def get_loaded_model2():
    return model2



# import torch
# def load_model(model_path):
#     device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#     model = ChatGLM(model_path=model_path)
#     # 将模型移动到指定的设备上
#     model.to(device)
#     model.load_model()
#     return model
    
# model_path = "../../../chatglm3"
# loaded_model=load_model(model_path)  # 加载模型

# # 提供已加载的模型
# def get_loaded_model():
#     return loaded_model