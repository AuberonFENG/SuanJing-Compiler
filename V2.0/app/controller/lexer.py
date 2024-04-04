import re
from flask import Flask, request, jsonify


class Token:
    """
    Token类用于表示文本中的一个词法单元（token）。

    Attributes:
        type (str): Token的类型，如'NUMBER'、'LEXEME'等，表示该token的词法角色。
        value (str): Token的值，即文本中token对应的具体字符串。
    """

    def __init__(self, type, value):
        """
        Token类的构造函数。

        Parameters:
            type (str): Token的类型。
            value (str): Token的值。
        """
        self.type = type
        self.value = value

    def __repr__(self):
        """
        生成Token的字符串表示形式。

        Returns:
            str: 表示Token的字符串，格式为"(type='token_type', value='token_value')"。
        """
        return f"(type='{self.type}', value='{self.value}')"


class SymbolTable:
    def __init__(self):
        # 使用字典来存储符号及其属性，这里的属性可以根据需要扩展
        self.symbols = {}

    def add_symbol(self, symbol, symbol_type, value=None):
        """
        添加一个符号到符号表中。

        :param symbol: 符号的文本表示。
        :param symbol_type: 符号的类型，例如 'UNIT' 或 'NUMBER'。
        :param value: 符号的附加值，可以根据需要存储额外信息。
        """
        self.symbols[symbol] = {'type': symbol_type, 'value': value}

    def get_symbol(self, symbol):
        """
        从符号表中获取一个符号的信息。

        :param symbol: 要查询的符号的文本表示。
        :return: 返回符号的信息，如果符号不存在则返回 None。
        """
        return self.symbols.get(symbol)

    def print_symbols(self):
        """
        打印符号表中所有符号的详细信息。
        """
        if not self.symbols:
            print("Symbol table is empty.")
            return
        for symbol, info in self.symbols.items():
            print(f"Symbol: {symbol}, Type: {info['type']}, Value: {info.get('value', 'N/A')}")


# 读取外部文件进入正则
def load_regex_from_file(file_path):
    """从指定的文件路径加载正则表达式字符串。"""
    with open(file_path, 'r', encoding='utf-8') as file:
        regex_pattern = file.read().replace('\n', '')
    return regex_pattern


class Lexer:
    def __init__(self):
        # 加载正则表达式
        regex_file_path = 'billion.txt'  # 替换为你的文件实际路径
        chinese_number_pattern = load_regex_from_file(regex_file_path)

        self.token_patterns = {
            'NUMBER': rf'({chinese_number_pattern})',
            'LEXEME': r'(今|又|有)',
            'TYPE': r'(田|广|从|周|径|弦|矢)',
            'PREFIX': r'(圭|邪|箕|圆|宛|弧|环|头|正|畔|舌|踵|下|中|外)',
            'UNIT': r'(步|里|人|钱)',
            'QUESTION': r'(问|为|馀|得|各|约之|合之|几何|减多益少|孰|多|而|平)',  # 孰多、孰少这些增强可以后面补
            'FUNCTION': r'(分|之|减其)',
            'PUNCTUATION': r'[，。？、]',
            'OTHER': r'[^一二三四五六七八九亿万千百十步里人钱今又有田广从周径弦失圭邪箕圆宛弧环头正畔舌踵下中外问为馀得各约之合之几何减多益少分之减其孰，。？、]+'  # 除本章以外的词
        }
        # 生成一个总的正则表达式，用于查找上述所有类型的标记
        self.token_regex = '|'.join(f'(?P<{type}>{pattern})' for type, pattern in self.token_patterns.items())

        # 定义状态转换表，用于指导如何根据当前标记类型转换到下一个状态
        self.state_transition_table = {
            'START': {'NUMBER': 'ERROR', 'LEXEME': 'LEXEME', 'TYPE': 'ERROR', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                      'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'NUMBER': {'NUMBER': 'ERROR', 'LEXEME': 'ERROR', 'TYPE': 'ERROR', 'PREFIX': 'PREFIX', 'UNIT': 'UNIT',
                       'QUESTION': 'ERROR', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'PUNCTUATION', 'OTHER': 'ERROR'},
            'LEXEME': {'NUMBER': 'NUMBER', 'LEXEME': 'LEXEME', 'TYPE': 'TYPE', 'PREFIX': 'PREFIX', 'UNIT': 'ERROR',
                       'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'TYPE': {'NUMBER': 'NUMBER', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                     'QUESTION': 'QUESTION', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'PUNCTUATION', 'OTHER': 'ERROR'},
            'PREFIX': {'NUMBER': 'ERROR', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                       'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'UNIT': {'NUMBER': 'NUMBER', 'LEXEME': 'ERROR', 'TYPE': 'ERROR', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                     'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'PUNCTUATION', 'OTHER': 'ERROR'},
            'QUESTION': {'NUMBER': 'ERROR', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'UNIT',
                         'QUESTION': 'QUESTION', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'PUNCTUATION', 'OTHER': 'ERROR'},
            'FUNCTION': {'NUMBER': 'NUMBER', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'UNIT',
                         'QUESTION': 'ERROR', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'PUNCTUATION': {'NUMBER': 'NUMBER', 'LEXEME': 'LEXEME', 'TYPE': 'TYPE', 'PREFIX': 'PREFIX', 'UNIT': 'ERROR',
                            'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'OTHER': {'NUMBER': 'ERROR', 'LEXEME': 'ERROR', 'TYPE': 'ERROR', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                      'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
        }
        # 确定初始状态
        self.current_state = 'START'
        # 初始化symbol_table
        # 在 Lexer 类的构造函数中初始化 SymbolTable 的实例
        self.symbol_table = SymbolTable()

    # 根据匹配到的文本返回对应的标记类型
    def get_token_type(self, match):
        for token_type, pattern in self.token_patterns.items():
            if re.fullmatch(pattern, match):
                return token_type
        return 'ERROR'

    # 对输入的文本进行标记化处理
    def tokenize(self, text):
        tokens = []
        for match in re.finditer(self.token_regex, text):
            token_value = match.group()
            token_type = self.get_token_type(token_value)
            if token_type == 'ERROR':
                print("lexer error detected")
                break  # 跳过无法识别的标记
            next_state = self.state_transition_table[self.current_state].get(token_type)
            if next_state == 'ERROR':
                print("lexer error detected")
                self.current_state = 'START'  # 遇到错误重置状态
                break
            else:
                self.current_state = next_state  # 转移到下一个状态
                token = Token(token_type, token_value)  # 创建 Token 实例
                tokens.append(token)  # 放进token中
                # 如果标记类型为 NUMBER 或 UNIT，将其添加到符号表中s
                if token_type in ['NUMBER', 'UNIT']:
                    self.symbol_table.add_symbol(token_value, token_type)
        return tokens

    #  单文本处理
    def tokenize_texts(self, texts):
        tokens = []  # 初始化一个空列表来存储所有的 tokens
        for text in texts:
            self.current_state = 'START'  # 重置 lexer 状态为 START
            tokens.extend(self.tokenize(text))  # 使用 extend 而不是 append 来添加元素
        return tokens

    # 单文本输出
    def format_and_display_results(self, tokens):
        formatted_results_with_numbers = []

        for i, token in enumerate(tokens, start=1):
            formatted_token = f"Token {i}: Type='{token.type}', Value='{token.value}'"
            formatted_results_with_numbers.append(formatted_token)

        # 显示格式化结果
        for formatted_result in formatted_results_with_numbers:
            print(formatted_result)

    # ----------------华丽的单多文本分界线-----------------

    # # 多文本处理
    # def tokenize_texts(self, texts):
    #     results = []
    #     for text in texts:
    #         self.current_state = 'START'  # 重置 lexer 状态为 START
    #         tokens = self.tokenize(text)  # 直接获取 tokens 列表
    #         results.append((text, tokens))  # 将 (text, tokens) 元组添加到结果中
    #     return results
    #
    # # 多文本输出
    # def format_and_display_results(self, results):
    #     formatted_results_with_numbers = []
    #
    #     for i, (text, tokens) in enumerate(results, start=1):
    #         formatted_text = f"Text {i}: {text}\nTokens:\n"
    #         formatted_tokens = "\n".join([f"  - {token.type}: '{token.value}'" for token in tokens])
    #         formatted_results_with_numbers.append(formatted_text + formatted_tokens)
    #
    #     # Displaying formatted results with numbers for the first few entries
    #     for formatted_result in formatted_results_with_numbers:
    #         print(formatted_result)
    #         print("\n---\n")


texts = [
    "今有田广九亿零八百七十六万五千四百三十二步，从八亿八千万零一千零三步。问为田几何？",
    # "又有田广十二步，从十四步。问为田几何？",
    # "今有田广一里，从一里。问为田几何？",
    # "又有田广二里，从三里。问为田几何？",
    # "今有十八分之十二。问约之得几何？",
    # "又有九十一分之四十九。问约之得几何？",
    # "今有三分之一，五分之二。问合之得几何？",
    # "又有三分之二，七分之四，九分之五。问合之得几何？",
    # "又有二分之一，三分之二，四分之三，五分之四。问合之得几何？",
    # "今有九分之八，减其五分之一。问馀几何？",
    # "又有四分之三，减其三分之一。问馀几何？",
    # "今有八分之五，二十五分之十六。问孰多？多几何？",
    # "又有九分之八，七分之六。问孰多？多几何？",
    # "又有二十一分之八，五十分之十七。问孰多？几何？",
    # "今有三分之一，三分之二，四分之三。问减多益少，各几何而平？",
    # "又有二分之一，三分之二，四分之三。问减多益少，各几何而平？",
    # "今有七人，分八钱三分钱之一。问人得几何？",
    # "又有三人，三分人之一，分六钱三分钱之一，四分钱之三。问人得几何？",
    # "今有田广七分步之四，从五分步之三。问为田几何？",
    # "又有田广九分步之七，从十一分步之九。问为田几何？",
    # "又有田广五分步之四，从九分步之五，问为田几何？",
    # "今有田广三步、三分步之一，从五步、五分步之二。问为田几何？",
    # "又有田广七步、四分步之三，从十五步、九分步之五。问为田几何？",
    # "又有田广十八步、七分步之五，从二十三步、十一分步之六。问为田几何？",
    # "今有圭田广十二步，正从二十一步。问为田几何？",
    # "又有圭田广五步、二分步之一，从八步、三分步之二。问为田几何？",
    # "今有邪田，一头广三十步，一头广四十二步，正从六十四步。问为田几何？",
    # "又有邪田，正广六十五步，一畔从一百步，一畔从七十二步。问为田几何？",
    # "今有箕田，舌广二十步，踵广五步，正从三十步。问为田几何？",
    # "又有箕田，舌广一百一十七步，踵广五十步，正从一百三十五步。问为田几何？",
    # "今有圆田，周三十步，径十步。问为田几何？",
    # "又有弧田，弦七十八步、二分步之一，矢十三步、九分步之七。问为田几何？",
    # "今有环田，中周九十二步，外周一百二十二步，径五步。问为田几何？"
]

# 对象初始化
lexer = Lexer()

# Call the function to tokenize the provided texts
# Processing all provided texts类中调用，文本处理
results = lexer.tokenize_texts(texts)

# 输出token结果
lexer.format_and_display_results(results)
# token对象的打印
print(results)
# 调用 print_symbols 方法来打印符号表中的所有符号及其详细信息
lexer.symbol_table.print_symbols()

# # 接入前端代码
# # 初始化 Flask 应用和 Lexer 实例
# app = Flask(__name__)
# lexer = Lexer()
#
# # 全局变量用于存储问题和答案
# inputstring = ''
# answer = 'test answer'
#
# from flask import g
#
#
# def get_question(question_text):
#     # 假设 Lexer 实例有一个 tokenize 方法返回处理结果
#     tokens = list(lexer.tokenize(question_text))
#     # 将处理结果保存到 g 对象中
#     g.tokens = tokens
#
#
# def push_answer():
#     # 从 g 对象获取处理结果
#     tokens = getattr(g, 'tokens', None)
#     if tokens is not None:
#         # 格式化处理结果
#         formatted_answer = ', '.join([f"{token_type}: '{token}'" for token_type, token in tokens])
#     else:
#         formatted_answer = "No question processed."
#     return formatted_answer
