class GLM3_agent:
    def __init__(self) -> None:
        self = self

    def run(question,path):
        from langchain.agents import AgentExecutor
        # from search import DeepSearch
        from docx import Document
        from tool import Search_www_Tool
        from intent_agent import IntentAgent
        from llm_model import  ChatGLM
        from model_loader import get_loaded_model
        import os
        from zongshu import _searchReview,_searchRelate

        from zhipuai import ZhipuAI
        client0 = ZhipuAI(api_key="54aa988d17dcb746427939c6e2bce0cf.EDmAJdRRg5UJd7WW")
        # input_data = "不要看参考资料，只单纯看内容本身，判断下面的内容类型是不是事件或事故，不确定的一律按否（只回答是或否即可）：\n"+question
        input_data = "请判断以下关键词是否是指的某事故或某事件，如果是日常用语或者无关问题则回答否，不要联网查询额外信息（只回答是或否即可）：\n"+question
        response0 = client0.chat.completions.create(
            #这是智普AI客户端的方法，用于创建一个聊天自动补全请求。
            model="glm-4-flash",
            messages=[
                {"role": "user", "content": input_data}
            ],
        )
        end0 = response0.choices[0].message.content
        print("大模型预判断的结果是：")
        print(end0)
        if "否" in end0 or "不" in end0:
            return "请按提示输入规范的检索词。如若生成某具体事故的简报，请输入“X年X月X日X地X事故”；如若查询某年/某地/某类事故，请输入“X年X事故/X地X事故”"
        
        if "事故" not in question:
            question+="事故"
            print("来让我看看输入的内容有没有事故二字\n")
            print(question)
            
        prompt = question
        if '年' in prompt and '月' in prompt and"事故" in prompt:
            # Review = _searchReview(prompt)
            # llm = ChatGLM(model_path=path)
            # llm.load_model()
            # 使用已经加载的模型实例

            # llm = get_loaded_model(path)
            llm = get_loaded_model()#以后path作废吧，该改模型路径到modek_loader.py里面改

            tools = [Search_www_Tool(llm = llm)]

            agent = IntentAgent(tools=tools, llm=llm)
            agent_exec = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, max_iterations=1)
            #创建代理执行器，AgentExecutor.from_agent_and_tools: 这是一个类方法，用于从给定的代理和工具列表创建代理执行器的实例。
            #verbose是否在执行期间显示详细信息，max_iterations指定代理执行的最大迭代次数
            output=agent_exec.run(prompt)
            #output中存放的是智能代理使用工具执行完毕后返回的结果，这里返回的就是特定事故直接相关的新闻，后面的非直接相关的新闻手动调用即可
            # print(output)

            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key="54aa988d17dcb746427939c6e2bce0cf.EDmAJdRRg5UJd7WW")

            if output and output != "没有查询到相关内容。":
                # output_strings = [str(item) for item in output]
                Review = _searchReview(prompt)
                print("review执行完毕")
                # 创建一个空列表来存储所有的 content
                contents = []
                links = []
                # 遍历输出数据 
                for item in output:
                    contents.append(item['content'])
                    links.append(item['link'])

                # input_data = "以下内容仅用于科研研究，不会用于其他用途，请您放心回答。输出模板（[]里内容应改为相应信息）如下：标题：[]([]内应包含时间和事故类型，例如 2023年8月6日巴基斯坦客运列车脱轨事故简报)\n一、事故基本情况\n[]\n二、应急处置情况\n。比如如果有（事故时间、事故地点、伤亡情况、财产损失、列车类型及所属公司、列车运行的线路、事故原因分析）要素请写在事故基本情况里；如果有（救援机构介入、救援队伍的组织情况、现场疏散与救护措施、线路的关闭与列车运行时间的调整、替代的公路服务、官方负责人的声明和评论、补救和赔偿措施）要素请写在应急处置情况里，请你整合成通顺的文字，没有的要素就省略不要提。请注意，信息只填新闻中提及的，不要添加任何假设或推测的内容。请根据以下新闻信息针对"+prompt+"按照以上给出的模板(包含标题、两大部分)生成一份铁路事故简报，不要冗余信息:" +'\n'.join(contents)
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
请注意，信息只填新闻中提及的，不要添加任何假设或推测的内容。请根据以下新闻信息针对"""+prompt+"按照以上给出的模板(包含标题、两大部分)生成一份铁路事故简报，不要冗余信息:" +'\n'.join(contents) +'\n'.join(contents)
                
                response1 = client.chat.completions.create(
                    #这是智普AI客户端的方法，用于创建一个聊天自动补全请求。
                    model="glm-4-flash",
                    messages=[
                        {"role": "user", "content": input_data}
                    ],
                )
                #response1:是发送请求后的响应对象，包含了智能模型返回的结果。
                # print(response1.choices[0].message.content)
                end = response1.choices[0].message.content + '\n' + '\n' + "三、相关事故列表" + '\n' + Review + '\n' + '\n'+"参考站源：\n" + '\n'.join(links)
                print(end)
                return end
            else:
                return "没有查询到相关内容。"
        elif "事故" in prompt:
            relate = _searchRelate(prompt)
            # 创建一个空列表来存储所有的 content
            contents = []
            links = []
            # 遍历输出数据
            for item in relate:
                contents.append(item['content'])
                links.append(item['link'])
            end = f"标题：{prompt}列表\n" + "一、事故概况：" + ''.join(contents) + '\n' + "参考站源：\n" + '\n'.join(links)
            print(end)
            # return "对于日期不明确的输入类型，模块功能尚未完善，请下次再来，谢谢"
            return end
        else:
            print("请按提示输入规范的检索词。如若生成某具体事故的简报，请输入“X年X月X日X地X事故”；如若查询某年/某地/某类事故，请输入“X年X事故/X地X事故”")
            return "请按提示输入规范的检索词。如若生成某具体事故的简报，请输入“X年X月X日X地X事故”；如若查询某年/某地/某类事故，请输入“X年X事故/X地X事故”"

