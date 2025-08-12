import requests
from bs4 import BeautifulSoup
import os
# from llm_model import ChatGLM
from model_loader import get_loaded_model


class RelatedSearch:
    def accidentsearch(self, query, num_results=20):
        subscriptionKey = '146f4e02b9b34f059f525833b206586f'
        customConfigId = '10f3ecd2-2628-4389-ac4d-f517c7b3f4c3'
        endpoint = 'https://api.bing.microsoft.com/'
        url = "https://api.bing.microsoft.com/v7.0/custom/search?q=" + query + "&mkt=zh-CN&customconfig=" + customConfigId

        headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
        all_results = []
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            search_results = response.json()
            organic_results = search_results.get('webPages', {}).get('value', [])

            for i, result in enumerate(organic_results[:num_results]):
                snippet = result.get('snippet')
                print(snippet)
                link = result.get('url', '')
                print(link)
                new_entry = {'snippet': snippet, 'link': link}
                all_results.append(new_entry)
                # all_results.append(response)
                print(f"结果{i + 1} 相关内容已保存。")
        except requests.exceptions.RequestException as e:
            print(f"向Bing自定义搜索API发出请求时出错:{e}")

        return all_results


def _searchReview(query):
    # 创建DeepSearch类的实例
    deep_search = RelatedSearch()

    prompt1 = f"请输出以下事件事故类型，不要带国家，直接输出xxx事故：'{query}'"
    llm = get_loaded_model()
    response1 = llm.generate_resp(prompt1)
    print(response1)

    # query1 = "各国" + response1 + "/2020、2021、2022、2023年度"
    query1 = "各国" + response1 + "历年"
    print(query1)
    all_results = deep_search.accidentsearch(query=query1)
    print(all_results)

    output = []
    for entry in all_results:
        snippet = entry.get('snippet', '')  # 如果'snippet'键不存在，则默认为空字符串
        link = entry.get('link', '')  # 如果'link'键不存在，则默认为空字符串

        print(f"Snippet: {snippet}")
        print(f"Link: {link}")
        # print()  # 打印空行以分隔不同的条目

        # prompt2 = f"以下内容是否包含事件发生的月日信息，输出是或否：{snippet}"
        if '月'not in snippet and '日'not in snippet:continue
        prompt2=f"判断以下内容是否是'{response1}'，请仔细核对确保一致，不确定的一律按否(只回答是或否):\n{snippet}{link}\n。"
        # response2 = llm.generate_resp(prompt2)
        # print(response2)        
        # print()
        from zhipuai import ZhipuAI
        client = ZhipuAI(api_key="54aa988d17dcb746427939c6e2bce0cf.EDmAJdRRg5UJd7WW")
        response2 = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "user", "content": prompt2}
            ],
            temperature=0.1
        )
        response2 = response2.choices[0].message.content
        print(response2)
        print()
        if "否" in response2 or "不" in response2:  # if "否" or "不" in response2:
            continue
        else:
            
            # prompt3 = f"请根据以下内容生成一句简洁的中文综述，正文没有明确年份的可以参考链接时间，具体日期还是根据文本，综述中只有开头有日期，其他部分不要出现年月日，不要出现“x”，如果出现请你自动删掉，综述格式为：xxxx年x月x日，某地xxx，发生xxx事故，事故原因是xxx，事故处置方式为xxx。：\n{snippet} {link}\n。"
            prompt3 = f"请根据以下内容生成一句简洁的中文综述，正文没有明确年份的可以参考链接时间，具体日期还是根据文本，综述中除开头的日期，其他部分不要出现年月日，只有开头有年月日，综述格式为：xxxx年x月x日，某地xxx，发生xxx事故，事故原因是xxx，事故处置方式为xxx。：\n{snippet} {link}\n。"

            llm = get_loaded_model()
            response3 = llm.generate_resp(prompt3)
            print(response3)
            day_pos = response3.find("日")
            day_pos1 = response3.find("月")
            if day_pos != -1:
                # 提取日期
                new_date = response3[:day_pos+1]# 检查这个日期是否已经存在于列表的"content"中
                new_date1 = response3[:day_pos1+1]
                date_exists = any(new_date1 in item for item in output)
                #如果日期不存在，则添加新事件到列表
                if not date_exists:
                    output.append(response3)
            else:
                #如果没有找到"日”，则直接添加到列表
                output.append(response3)

        if len(output) >= 5:
            break
    output1 = '\n'.join(output)
    print("模块一综述部分的output1开始！！！！！！！")
    print(output1)
    print("************************************")
    return output1

def _searchRelate(query):
    # 创建DeepSearch类的实例
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key="54aa988d17dcb746427939c6e2bce0cf.EDmAJdRRg5UJd7WW")
    # prompt233=f"请对以下关键词进行修改，如果只有年份没有国家信息，则在关键词前面加上各国；如果只包含地区信息没有年份，则在关键词后面加上2020/2021/2022/2023年；如果年份和地区信息都没有，则在关键词前面加上各国，后面加上2020/2021/2022/2023年；如果年份和地区信息都有，则关键词不变，直接输出更改后的关键词，不要解释：{query}"
    # response233 = client.chat.completions.create(
    #     model="glm-4",
    #     messages=[
    #         {"role": "user", "content": prompt233}
    #     ],
    #     temperature=0.1
    # )
    # response233 = response233.choices[0].message.content
    # print(response233)
    # print("here\n\n\n\n\nhere")
    # print(response233)
    if '年' not in query:
        query = query + "历年"
    # response233=query
    deep_search = RelatedSearch()
    all_results = deep_search.accidentsearch(query=query)
    print(all_results)
    llm = get_loaded_model()
    output_list = []
    for entry in all_results:
        snippet = entry.get('snippet', '')  # 如果'snippet'键不存在，则默认为空字符串
        link = entry.get('link', '')  # 如果'link'键不存在，则默认为空字符串

        print(f"Snippet: {snippet}")
        print(f"Link: {link}")
        # print()  # 打印空行以分隔不同的条目
        if '月'not in snippet and '日'not in snippet:
            continue
        prompt2=f"判断以下内容是否是'{query}'事件，请仔细核对年份和地点，不确定的一律按否（只回答是或否）：\n{snippet}{link}\n"
        # prompt2 = f"以下内容是否包含事件发生的年月日信息，输出是或否：{snippet}"
        # response2 = llm.generate_resp(prompt2)
        # print(response2)
        # prompt2 = f"请根据提供的信息仔细核对以下内容是否与'{query}'相匹配。如果年份或者地点或者事件描述与查询不完全一致，请回答'否'。只回答是或否：\n{snippet}\n"  
        # prompt2=f"请根据提供的信息仔细核对以下内容是否与'{query}'相匹配。如果年份地点或事件描述与查询不完全一致，请回答'否'。只回答是或否：\n{snippet}{link}\n"
        response2 = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "user", "content": prompt2}
            ],
            temperature=0.1
        )
        response2 = response2.choices[0].message.content
        print(response2)
        print()

        if "否" in response2 or "不" in response2:  # if "否" or "不" in response2:
            continue
        else:
            prompt3 = f"请根据以下内容生成一句关于{query}的中文综述，格式为：xxxx年x月x日，某地xxx，发生xxx事故，事故原因是xxx，事故处置方式为xxx。正文没有明确年份的可以参考链接时间，具体日期还是根据文本，年月日开头，切记只有开头有日期，后续不要出现具体日期，不能用资讯发布日期作为事故日期：\n{snippet} {link}\n。"
            # llm = get_loaded_model()
            response3 = llm.generate_resp(prompt3)
            print(response3)
            print("\nthis little dialogue is over")
            day_pos = response3.find("日")
            day_pos1 = response3.find("月")
            if day_pos != -1:
                # 提取日期
                new_date = response3[:day_pos+1]# 检查这个日期是否已经存在于列表的"content"中
                new_date1 = response3[:day_pos1+1]
                date_exists = any(new_date1 in item["content"] for item in output_list)
                #如果日期不存在，则添加新事件到列表
                if not date_exists:
                    output_list.append({"content": response3,"link": link})
            else:
                #如果没有找到"日”，则直接添加到列表
                output_list.append({"content": response3, "link": link})
            # output_list.append({"content": response3, "link": link})

        if len(output_list) >= 8:
            break

    # output1 = '\n'.join([entry['output'] for entry in output_list])
    # print(output1)
    # if output_list == []:
    #     return [{"content": "未检索到相关事故。","link": "None"}]
    return output_list