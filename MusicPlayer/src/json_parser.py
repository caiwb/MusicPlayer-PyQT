# -*- encoding:utf-8 -*-

import string

class Stack:

    def __init__(self):
        self.items = []

    def top(self):
        if self.size() > 0:
            return self.items[self.size() - 1]

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

    def showItems(self):
        print self.items

class JsonParser:

    def __init__(self):
        self.data = {}

    def load(self, s):

        if not isinstance(s, str) or len(s) < 2 or s[0] != '{' or s[len(s) - 1] != '}':
            raise Exception("this string is not a json string!")
            return

        stack = Stack()

        #string
        wordStr = ""
        strStart = -1
        strEnd = -1

        #number
        number = 0
        numberStart = -1
        numberEnd = -1
        isFloat = False

        loopCount = 0

        for c in s:
            list = stack.items
            o = ord(c)
            if (c == '-' or c == '.' or (c >= '0' and c <= '9')) and strStart == -1:# 处理数字
                if numberStart == -1:
                    numberStart = loopCount
                if c == '.':#小数
                    isFloat = True
            else:
                if numberStart != -1 and numberEnd == -1:
                    numberEnd = loopCount
                    if isFloat:
                        number = string.atof(s[numberStart : numberEnd])
                    else:
                        number = string.atoi(s[numberStart : numberEnd])
                    stack.push(number)
                    number = 0
                    numberStart = -1
                    numberEnd = -1
                    isFloat = False# 处理数字end

                if c == '{'or c == '[' or c == ',':
                    stack.push(c)

                elif c == '"':# 处理字符串
                    if strStart == -1:
                        strStart = loopCount + 1
                    else:
                        strEnd = loopCount
                        wordStr = s[strStart : strEnd]
                        stack.push(wordStr)
                        wordStr = ""
                        strStart = -1
                        strEnd = -1

                elif c == 'n' and strStart == -1:# 处理null
                    if s[loopCount : loopCount + 4] == 'null':
                        stack.push(None)

                elif c == '}':
                    result = {}
                    while stack.top() != '{' and stack.size() > 1:
                        value = stack.pop()
                        key = stack.pop()
                        result.update({key : value})
                        if stack.top() == ',':
                            stack.pop()
                            continue
                    if stack.top() == '{':
                        stack.pop()
                    stack.push(result)

                elif c == ']':
                    # list = stack.items
                    result = []
                    while stack.top() != '[' and stack.size() > 0:
                        result.insert(0, stack.pop())
                        if stack.top() == ',':
                            stack.pop()
                            continue
                    if stack.top() == '[':
                        stack.pop()
                    stack.push(result)

            loopCount += 1

        # stack.showItems()
        # i = stack.size()
        # list = stack.items
        if stack.size() == 1:
            self.data = stack.pop()
            # self.__convertStringToUnicode(None, None, self.data)
        else:
            raise Exception("this string is not a json string!")

    def dump(self):
        jsonStr = self.__convertDataToJson(self.data)

        return jsonStr.encode("utf-8")

    def __convertDataToJson(self, object):
        if isinstance(object, str) or isinstance(object, unicode):
            return '"%s"'% object
        elif isinstance(object, int):
            return '%d' % object
        elif isinstance(object, float):
            return '%f' % object
        elif not object:
            return 'null'
        elif isinstance(object, dict):
            s = '{'
            loopCount = 0
            for key in object.keys():
                if isinstance(key, str) or isinstance(key, unicode):
                    s += '"%s":'% key
                elif isinstance(key, int):
                    s += '%d'% key
                elif isinstance(key, float):
                    s += '%f'% key
                s += self.__convertDataToJson(object[key])
                if loopCount < len(object.keys()) - 1:
                    s += ','
                else:
                    s += '}'
                loopCount += 1
            return s
        elif isinstance(object, list):
            s = '['
            loopCount = 0
            for item in object:
                s += self.__convertDataToJson(item)
                if loopCount < len(object) - 1:
                    s += ','
                else:
                    s += ']'
                loopCount += 1
            return s

    def dumpJson(self, f):
        # jsonStr = str(self.data).encode("UTF-8")
        # jsonStr = self.__checkJsonString(jsonStr)
        jsonStr = self.dump()

        try:
            file = open(f, 'w')
            file.write(jsonStr)
        except Exception as e:
                raise ValueError(e)
        finally:
            file.close()

    def loadJson(self, f):
        try:
            file = open(f)
            jsonStr = file.read()
        except Exception as e:
            raise ValueError(e)
        finally:
            self.load(jsonStr)
            file.close()

    def loadDict(self, d):
        if not isinstance(d, dict):
            raise Exception("param is not a dict!")
            return
        self.data.update(d)

    def dumpDict(self):
        dictUnicode = self.data
        self.__convertStringToUnicode(None, None, dictUnicode)
        return dictUnicode

    def __convertUnicodeToString(self, object, key, value):
        if isinstance(value, dict):
            for k in value.keys():
                if isinstance(k, unicode):
                    v = value[k]
                    value.pop(k)
                    k = k.encode("utf-8")
                    value[k] = v
                    self.__convertUnicodeToString(value, k, v)

        elif isinstance(value, unicode):
            object[key] = value.encode("utf-8")

        elif isinstance(value, list):
            for item in value:
                self.__convertUnicodeToString(object, key, item)

    def __convertStringToUnicode(self, object, key, value):
        if isinstance(value, dict):
            for k in value.keys():
                if isinstance(k, str):
                    v = value[k]
                    value.pop(k)
                    k = k.decode("utf-8")
                    value[k] = v
                    self.__convertStringToUnicode(value, k, v)

        elif isinstance(value, str):
            object[key] = value.decode("utf-8")

        elif isinstance(value, list):
            for item in value:
                self.__convertStringToUnicode(object, key, item)

    def update(self, d):
        if not isinstance(d, dict):
            raise Exception("param is not a dict!")
            return
        self.data.update(d)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            return
        self.data.update({key: value})











