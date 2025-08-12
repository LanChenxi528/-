import requests
from requests.exceptions import RequestException, Timeout
from bs4 import BeautifulSoup
#用于解析HTML文档。
import os
# from llm_model import ChatGLM
from model_loader import get_loaded_model
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException, Timeout
os.environ["subscriptionKey"] = "146f4e02b9b34f059f525833b206586f"#"146f4e02b9b34f059f525833b206586f"#146是lcx"856bed55c3f44e7facac61212edce159"

#通过必应搜索API和预训练的语言模型来进行深度搜索
class DeepSearch:
    def __init__(self):
        # self.model_path = "/home/wzq/chatglm3/chatglm3-6b"  # 大模型路径
        # self.llm = ChatGLM(model_path=self.model_path)
        # self.llm.load_model()  # 加载大模型

        # 使用已经加载的模型实例***!!!
        self.llm = get_loaded_model()

    def search(self, query, num_results=3, site="zh.wikipedia.org"):
        all_contents = self._search(query, num_results, site)
        print("中文搜索已结束\n")
        
        # 如果没有找到相关内容，尝试翻译成英文再次搜索
        if not all_contents:
            print("尝试翻译查询内容为英文并再次搜索...")
            prompt1 = f"请将以下内容翻译成英文：{query}"
            en_query = self.llm.generate_resp(prompt1)
            print("英文为：")
            print(en_query)
            all_contents = self._search(en_query, num_results, site)            
        if not all_contents:
            return "没有查询到相关内容。"        
        return all_contents
    

    # def _process_result(self, result,query):
    #     snippet = result.get('snippet')
    #     link = result.get('url', '')
    #     try:
    #         response = requests.get(link, timeout=10)
    #         response.raise_for_status()
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #         paragraphs = soup.find_all('p')
    #         if paragraphs:
    #             full_content = "\n".join([p.get_text(separator=' ', strip=True) for p in paragraphs])
    #             full_content = snippet + full_content
    #             print(full_content)
    #             full_content = full_content[:5000]
    #             prompt = f"判断以下内容是否是'{query}'事件，请仔细核对时间地点，不确定的一律按否（只回答是或否）：\n{full_content}\n。"
    #             response = self.llm.generate_resp(prompt)
    #             print(response)
    #             if "否" in response or "不" in response:
    #                 print(f"结果 内容不相关，已删除。")
    #             else:
    #                 return {'title': result.get('name', ''), 'content': full_content, 'link': link}
    #         else:
    #             print(f"找不到页面内容.")
    #     except requests.exceptions.RequestException as e:
    #         print(f"向页面发出请求时出错 {link}: {e}")
    #     return None

    # def _search(self, query, num_results=3, site="zh.wikipedia.org"):
    #     subscriptionKey = os.environ.get('subscriptionKey')
    #     endpoint = 'https://api.bing.microsoft.com/v7.0/custom/search'
    #     customConfigId = 'bfe68edd-cc55-4576-8284-09cc818a459f'
    #     url = f"https://api.bing.microsoft.com/v7.0/custom/search?q="+ query + "&customconfig=" + customConfigId
    #     headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
    #     all_results = []
    #     try:
    #         response = requests.get(url, headers=headers, timeout=10)
    #         response.raise_for_status()
    #         search_results = response.json()
    #         organic_results = search_results.get('webPages', {}).get('value', [])
    #         with ThreadPoolExecutor(max_workers=num_results) as executor:
    #             futures = [executor.submit(self._process_result, result, query) for result in organic_results[:num_results]]
    #             for future in as_completed(futures):
    #                 result = future.result()
    #                 if result:
    #                     all_results.append(result)
    #                     print(f"相关内容已保存。")
    #     except (RequestException, Timeout) as e:
    #         print(f"请求超时或出错: {e}")
    #     return all_results


    #执行实际的搜索操作，使用 Bing 自定义搜索 API 搜索相关内容。
    def _search(self, query, num_results=3, site="zh.wikipedia.org"):
        subscriptionKey = os.environ.get('subscriptionKey')
        #从环境变量中获取 Bing API 的订阅密钥。
        endpoint = 'https://api.bing.microsoft.com/v7.0/custom/search'
        #指定 Bing 自定义搜索 API 的端点。
        customConfigId = '10f3ecd2-2628-4389-ac4d-f517c7b3f4c3'#'10f3ecd2-2628-4389-ac4d-f517c7b3f4c3'#10f是lcx'bfe68edd-cc55-4576-8284-09cc818a459f'
        #指定自定义配置的 ID。
        # url = f"{endpoint}?q={query}&customconfig={customConfigId}"
        url = f"https://api.bing.microsoft.com/v7.0/custom/search?q="+ query + "&customconfig=" + customConfigId

        headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
        #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.59 Safari/537.36 Edg/91.0.864.59'
        #
        #设置 HTTP 请求的头部信息，包括订阅密钥。

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            #检查请求的响应状态，如果状态码不是 200，则抛出异常。

            search_results = response.json()
            #将响应的 JSON 数据解析为 Python 字典。
            organic_results = search_results.get('webPages', {}).get('value', [])
            #Bing API 的响应数据通常包含多种类型的搜索结果，其中 'webPages' 键用于表示网页搜索结果。
            #接着，再次使用 .get() 方法从 'webPages' 对应的字典中获取键为 'value' 的值
            #在 Bing API 的响应中，搜索结果以列表的形式存储在 'value' 键对应的值中
            #organic_results是个列表，这里的列表就是我们所需要的有机搜索结果列表。

            # all_contents = ""
            all_results = []
            for i, result in enumerate(organic_results[:num_results]):
            #enumerate() 是一个 Python 内置函数，它用于将可迭代对象中的元素组合为一个索引序列，同时列出数据和数据下标。
            #在这种情况下，enumerate(organic_results[:num_results]) 将有机搜索结果列表 organic_results 中的元素与它们的索引配对起来，并且限制遍历的数量为 num_results。
            #enumerate() 函数返回一个迭代器，该迭代器生成包含两个元素的元组 (index, item)，其中 index 是元素的索引，item 是元素本身。
            #在每次迭代时，enumerate() 函数会返回下一个索引和对应的元素。
                snippet = result.get('snippet')
                link = result.get('url', '')
                #从每个结果中提取链接。
                try:
                    response = requests.get(link, timeout=10)
                    #发送 HTTP GET 请求到链接，获取页面内容。
                    response.raise_for_status()
                    #检查请求的响应状态，如果状态码不是 200，则抛出异常。
                    soup = BeautifulSoup(response.text, 'html.parser')
                    #使用 BeautifulSoup 解析HTML页面内容。
                    # soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
                    paragraphs = soup.find_all('p')#['p', 'span']
                    # paragraphs = soup.find_all(['p', 'span'])#['p', 'span']
                    
                    #找到页面中所有的段落元素。
                    if paragraphs:#成功提取了段落内容。
                        # full_content = snippet.join([p.get_text(separator=' ', strip=True) for p in paragraphs])
                        full_content = "\n".join([p.get_text(separator=' ', strip=True) for p in paragraphs])
                        full_content = snippet + full_content
                        #将每个段落的文本连接起来，构成完整的页面内容。
                        # 这里使用了列表推导式和 join() 方法来生成字符串，
                        # 列表推导式从每个段落元素中提取文本，
                        # join() 方法将这些文本用换行符连接起来。
                        #列表推导式是一种在Python中用来简洁地创建列表的方法。[expression for item in iterable if condition]
                        #这是生成列表元素的表达式：p.get_text(separator=' ', strip=True)，该方法使用空格作为分隔符连接元素中的文本，并将其剥离首尾的空格。
                        print(full_content)
                        full_content=full_content[:5000]
                        prompt = f"判断以下内容是否是'{query}'事件，请仔细核对时间地点，不确定的一律按否（只回答是或否）：\n{full_content}\n。"
                        response = self.llm.generate_resp(prompt)
                        print(response)
                        if "否" in response or "不" in response:
                            print(f"结果{i+1} 内容不相关，已删除。")
                        else:
                            # all_contents += f"结果{i+1}:\n{full_content}\n\n"
                            all_results.append({'title': result.get('name', ''), 'content': full_content, 'link': link})
                            #如果提取的内容与查询相关，则将标题、内容和链接添加到 all_results 列表中，并输出相关信息。
                            print(f"结果{i+1} 相关内容已保存。")
                    else:
                        print(f"结果 {i+1}: 找不到页面内容.")
                except requests.exceptions.RequestException as e:
                    print(f"向页面发出请求时出错 {link}: {e}")
                    # break
        # except requests.exceptions.RequestException as e:
        #     print(f"向Bing自定义搜索API发出请求时出错:{e}")
        except (RequestException, Timeout) as e:
            print(f"请求超时或出错: {e}")
            return []

        # return all_contents
        return all_results
