import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL_DM = "https://api.qqsuu.cn/api/dm-dream" #https://api.qqsuu.cn/

@plugins.register(name="zhougong",
                  desc="周公解梦",
                  version="1.0",
                  author="wyh",
                  desire_priority=100)




class zhougong(Plugin):

    content = None
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"发送【周公解梦 梦境内容】 或者 【梦到 梦境内容】进行解梦"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        
        if self.content.startswith("周公解梦") or self.content.startswith("梦到") or self.content.startswith("梦见"):
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = self.zhougong()
            if result != None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS


    def zhougong(self):
        url = BASE_URL_DM
        # params = "type=json"
        if self.content.startswith("周公解梦"):
            params = {"num":1, "word":self.content.replace(" ", "")[4:]}
        else:
            params = {"num":1, "word":self.content.replace(" ", "")[2:]}
            
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        try:
            # 主接口
            response = requests.get(url=url, params=params, headers=headers,timeout=2)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get('code') == 200 and  json_data['data']['list']:
                    data = json_data['data']['list'][:10]
                    logger.info(json_data)
                                        
                    i = 0
                    text = ("周公解梦结果：\n" "--------------------")
                    while i < len(data):
                        line = f"\n【{i+1}】:{data[i]['title']}\n🔗:{data[i]['result']}\n"
                        line.replace("<br>","\n")
                        text+=line
                        i+=1
                  
                    return text
                else:
                    logger.error(f"主接口返回值异常:{json_data}")
                    raise ValueError('not found')
            else:
                logger.error(f"主接口请求失败:{response.text}")
                raise Exception('request failed')
        except Exception as e:
            logger.error(f"接口异常：{e}")
                
        logger.error("所有接口都挂了,无法获取")
        return None


