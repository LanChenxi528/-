from typing import List, Tuple, Any, Union
from langchain.schema import AgentAction, AgentFinish
from langchain.agents import BaseSingleActionAgent
#BaseSingleActionAgent 类，它是一个单动作代理的基类，来自 langchain.agents 模块。
from langchain import LLMChain, PromptTemplate
#LLMChain 和 PromptTemplate 类，它们分别用于使用语言模型链和创建提示模板
from langchain.base_language import BaseLanguageModel


class IntentAgent(BaseSingleActionAgent):
    tools: List#存储工具的列表。
    llm: BaseLanguageModel#存储语言模型的实例。
    intent_template: str = """
    现在有一些意图，类别为{intents}，你的任务是根据用户的query内容找到最匹配的意图类；只需调用一次tool，回复的意图类别必须在提供的类别中，并且必须按格式回复：“意图类别：<>”。
    
    举例：
    问题：The Swedish passenger train derailed accident on August 7, 2023
    意图类别：互联网检索查询

    问题：2023年8⽉7⽇瑞典客运列⻋脱轨事故
    意图类别：互联网检索查询

    问题：“{query}”
    """
    #定义了意图识别任务的模板。
    prompt = PromptTemplate.from_template(intent_template)
    llm_chain: LLMChain = None
    #prompt: PromptTemplate：根据模板创建的提示模板。
    #llm_chain: LLMChain：用于存储语言模型链的实例。
    def get_llm_chain(self):#创建语言模型链实例
        if not self.llm_chain:
            self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def choose_tools(self, query) -> List[str]:
        self.get_llm_chain()
        tool_names = [tool.name for tool in self.tools]
        tool_descr = [tool.name + ":" + tool.description for tool in self.tools]
        resp = self.llm_chain.predict(intents=tool_names, query=query)
        #使用语言模型链 llm_chain 来预测给定查询的意图。predict 方法会返回一个列表，包含了对于每个意图的预测得分。
        select_tools = [(name, resp.index(name)) for name in tool_names if name in resp]
        #将工具名称与其在预测列表中的索引位置关联起来。
        select_tools.sort(key=lambda x:x[1])
        #根据工具在预测列表中的索引位置对工具进行排序，以确保索引位置较小（即预测得分较高）的工具排在前面。
        return [x[0] for x in select_tools]

    @property
    def input_keys(self):
        return ["input"]


    
    def plan(
            self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        # 直接选择工具并返回工具的执行结果
        tool_names = self.choose_tools(kwargs["input"])
        if tool_names:  # 检查列表是否不为空
            tool_name = tool_names[0]
            tool_input = kwargs["input"]#获取查询作为工具的输入。
            # 获取工具的实例
            tool = next(tool for tool in self.tools if tool.name == tool_name)
            # 执行工具并获取结果
            tool_result = tool._run(tool_input)
            return_values = {'output': tool_result}
            # return AgentFinish(return_values=return_values, log=tool_result)
            return AgentFinish(return_values=return_values, log=str(tool_result))
        #返回一个 AgentFinish 对象，其中包含了工具的执行结果以及相应的日志信息，工具执行结果以字符串形式存储
        else:
            # 处理没有可用工具的情况
            return AgentFinish(return_values={'output': "No suitable tool found."}, log="")

    async def aplan(
            self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[List[AgentAction], AgentFinish]:
        raise NotImplementedError("IntentAgent does not support async")
       