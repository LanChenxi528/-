from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from typing import Optional#用于表示可选类型的参数。
from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
import re, random
from hashlib import md5
from search import DeepSearch
import os

class functional_Tool(BaseTool):
    name: str = ""
    description: str = ""
    # url: str = ""

    # def _call_func(self, query):
    #     raise NotImplementedError("subclass needs to overwrite this method")

    def _run(
            self,
            query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return self._call_func(query)

    async def _arun(
            self,
            query: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("APITool does not support async")


class Search_www_Tool(functional_Tool):
    llm: BaseLanguageModel

    # tool description  工具的名称和描述信息。
    name = "互联网检索查询"
    description = "根据用户问题搜索最新的结果，并返回搜索的详细内容"
    
    # QA params 用于构建问题和回答的模板。
    qa_template = """
    请根据下面信息```{text}```，回答问题：{query}
    """
    prompt = PromptTemplate.from_template(qa_template)
    llm_chain: LLMChain = None
    '''
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None):
        self.get_llm_chain()
        context = DeepSearch.search(query = query)
        resp = self.llm_chain.predict(text=context, query=query)
        return resp
    '''
    def _run(
            self,
            query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        # 使用回调管理器记录输出
        if run_manager:
            run_manager.on_tool_start(tool_name=self.name, args=query)
        
        # context = DeepSearch.search(query=query)
        # if run_manager:
        #     run_manager.on_tool_end(output=context)
        # return context
        
        # 创建DeepSearch实例
        deep_search_instance = DeepSearch()
        
        # 使用DeepSearch实例调用search方法
        context = deep_search_instance.search(query=query)
        
        if run_manager:
            run_manager.on_tool_end(output=context)
        return context

    # def _call_func(self, query) -> str:
    #     self.get_llm_chain()
    #     context = DeepSearch.search(query = query)
    #     # print(context)
    #     # resp = self.llm_chain.predict(text=context, query=query)
    #     # print(resp)
    #     # return resp
    #     return context
    

    # def get_llm_chain(self):
    #     if not self.llm_chain:
    #         self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)