# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import os


class ReportGenerator:
    def __init__(self):
        
        self._register_chinese_fonts()
        self.default_font = "Helvetica"
        self.bold_font = "Helvetica-Bold"
        self.chinese_font_available = False
        self.script_path = os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(self.script_path, '../resource/images/logo.png')

        if "SimSun" in pdfmetrics.getRegisteredFontNames():
            self.default_font = "SimSun"
            self.chinese_font_available = True
            if "SimHei" in pdfmetrics.getRegisteredFontNames():
                self.bold_font = "SimHei"
            else:
                self.bold_font = "SimSun"  # Fallback bold to SimSun if SimHei not found
                print("警告: 未找到SimHei字体，粗体将使用SimSun。")
        else:
            print("警告: 未找到SimSun中文字体，将使用默认英文字体，中文可能显示为方框。")

        # Page layout constants
        self.PAGE_WIDTH, self.PAGE_HEIGHT = A4  # Using A4 size
        self.MARGIN_TOP = 0.75 * inch
        self.MARGIN_BOTTOM = 0.75 * inch
        self.MARGIN_LEFT = 0.75 * inch
        self.MARGIN_RIGHT = 0.75 * inch
        self.CONTENT_WIDTH = self.PAGE_WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT

        self.TITLE_FONT_SIZE = 18
        self.SECTION_TITLE_FONT_SIZE = 14
        self.CONTENT_FONT_SIZE = 10
        self.SMALL_FONT_SIZE = 9

        self.LINE_HEIGHT_LARGE = 18
        self.LINE_HEIGHT_NORMAL = 14
        self.LINE_HEIGHT_SMALL = 12
        self.SECTION_SPACING = 10  # Points between sections
        self.ITEM_SPACING = 5  # Points between items in a list

    def _register_chinese_fonts(self):
        """注册中文字体"""
        try:
            # Windows系统字体路径
            windows_font_dir = "C:/Windows/Fonts/"
            registered_simsun = False
            registered_simhei = False

            if os.path.exists(windows_font_dir):
                simsun_path_ttc = os.path.join(windows_font_dir, "simsun.ttc")
                simsun_path_ttf = os.path.join(windows_font_dir, "simsun.ttf")
                simhei_path_ttf = os.path.join(windows_font_dir, "simhei.ttf")

                if os.path.exists(simsun_path_ttc):
                    pdfmetrics.registerFont(TTFont("SimSun", simsun_path_ttc))
                    registered_simsun = True
                elif os.path.exists(simsun_path_ttf):
                    pdfmetrics.registerFont(TTFont("SimSun", simsun_path_ttf))
                    registered_simsun = True

                if os.path.exists(simhei_path_ttf):
                    pdfmetrics.registerFont(TTFont("SimHei", simhei_path_ttf))
                    registered_simhei = True

            if not registered_simsun:
                # Attempt to find common macOS paths for SimSun
                macos_font_paths = [
                    "/Library/Fonts/Songti.ttc",  # SC
                    "/System/Library/Fonts/Supplemental/Songti.ttc",
                ]
                for p in macos_font_paths:
                    if os.path.exists(p):
                        try:
                            pdfmetrics.registerFont(
                                TTFont("SimSun", p, subfontIndex=0)
                            )  # Try first font in collection
                            registered_simsun = True
                            print(f"Info: Registered SimSun from {p}")
                            break
                        except Exception as e_mac_font:
                            print(
                                f"Info: Could not register {p} as SimSun: {e_mac_font}"
                            )

            if not registered_simhei:
                # Attempt to find common macOS paths for SimHei / Heiti
                macos_font_paths_hei = [
                    "/Library/Fonts/Hei.ttf",  # STHeiti
                    "/System/Library/Fonts/Supplemental/STHeiti Medium.ttc",
                    "/System/Library/Fonts/PingFang.ttc",  # PingFang SC Regular might be an alternative
                ]
                for p in macos_font_paths_hei:
                    if os.path.exists(p):
                        try:
                            # For TTC, you might need to specify subfontIndex
                            idx = 0 if "PingFang" in p else 0  # common subfont index
                            pdfmetrics.registerFont(
                                TTFont("SimHei", p, subfontIndex=idx)
                            )
                            registered_simhei = True
                            print(f"Info: Registered SimHei (or alternative) from {p}")
                            break
                        except Exception as e_mac_font_h:
                            print(
                                f"Info: Could not register {p} as SimHei: {e_mac_font_h}"
                            )

            if not registered_simsun:
                print("警告: 未找到SimSun或兼容中文字体。")
            if not registered_simhei:
                print("警告: 未找到SimHei或兼容中文粗体。")

        except Exception as e:
            print(f"字体注册过程中发生错误: {e}")

    def _draw_logo(self, canvas, x, y, max_width=1.5 * inch, max_height=0.75 * inch):
        if os.path.exists(self.logo_path):
            try:
                img = ImageReader(self.logo_path)
                img_width, img_height = img.getSize()
                aspect = img_height / float(img_width)

                display_width = max_width
                display_height = display_width * aspect

                if display_height > max_height:
                    display_height = max_height
                    display_width = display_height / aspect

                canvas.drawImage(
                    self.logo_path,
                    x,
                    y - display_height,
                    width=display_width,
                    height=display_height,
                    preserveAspectRatio=True,
                    anchor="nw",
                )
                return y - display_height - self.ITEM_SPACING  # Return new y position
            except Exception as e:
                print(f"错误: 无法加载或绘制logo '{self.logo_path}': {e}")
                return y  # Return original y if error
        else:
            print(f"警告: Logo文件未找到 '{self.logo_path}'")
            return y  # Return original y if no logo

    def _draw_header(self, canvas, title_text):
        canvas.setFont(self.bold_font, self.TITLE_FONT_SIZE)
        title_width = canvas.stringWidth(
            title_text, self.bold_font, self.TITLE_FONT_SIZE
        )
        canvas.drawCentredString(
            self.PAGE_WIDTH / 2, self.PAGE_HEIGHT - self.MARGIN_TOP, title_text
        )
        return (
            self.PAGE_HEIGHT
            - self.MARGIN_TOP
            - self.TITLE_FONT_SIZE
            - self.SECTION_SPACING * 2
        )  # Extra spacing after title

    def _draw_section_title(self, canvas, title, y_pos):
        canvas.setFont(self.bold_font, self.SECTION_TITLE_FONT_SIZE)
        canvas.drawString(self.MARGIN_LEFT, y_pos, title)
        return y_pos - self.SECTION_TITLE_FONT_SIZE - self.ITEM_SPACING

    def _draw_key_value_pairs(self, canvas, data_dict, y_pos, two_column_threshold=30):

        canvas.setFont(self.default_font, self.CONTENT_FONT_SIZE)
        x_pos = self.MARGIN_LEFT + 1 * inch  # Indent content
        col_width = (
            self.CONTENT_WIDTH - 1 * inch
        ) / 2 - self.ITEM_SPACING
        current_x = x_pos
        start_y_of_line = y_pos

        keys_order = [
            "姓名",
            "性别",
            "年龄",
            "血型",
            "身高",
            "体重",
            "联系方式",
            "邮箱",
            "紧急联系人",
            "记录时间",
        ] 

        items_in_current_line = 0
        for key in keys_order:
            value = data_dict.get(key, "N/A")
            if value is None:
                value = "N/A"
            if not isinstance(value, str):
                value = str(value)

            item_text = f"{key}: {value}"
            item_width = canvas.stringWidth(
                item_text, self.default_font, self.CONTENT_FONT_SIZE
            )

            if items_in_current_line == 1 and (current_x + item_width) < (
                self.MARGIN_LEFT + self.CONTENT_WIDTH - self.ITEM_SPACING
            ):

                canvas.drawString(current_x, start_y_of_line, item_text)
                y_pos = start_y_of_line - self.LINE_HEIGHT_NORMAL
                current_x = x_pos
                items_in_current_line = 0
            else:

                canvas.drawString(x_pos, y_pos, item_text)
                if (
                    item_width > col_width or items_in_current_line == 1
                ):
                    y_pos -= self.LINE_HEIGHT_NORMAL
                    current_x = x_pos
                    items_in_current_line = 0
                else:
                    current_x = x_pos + col_width + self.ITEM_SPACING
                    start_y_of_line = (
                        y_pos
                    )
                    items_in_current_line = 1

        if items_in_current_line == 1:
            y_pos -= self.LINE_HEIGHT_NORMAL

        return y_pos - self.ITEM_SPACING

    def _draw_multiline_text(self, canvas, text_content, y_pos, indent=True):
        canvas.setFont(self.default_font, self.CONTENT_FONT_SIZE)
        x_pos = self.MARGIN_LEFT + (1 * inch if indent else 0)
        if text_content:
            lines = str(text_content).split("\n")
            for line in lines:

                words = line.split(" ")
                current_line = ""
                line_width_limit = self.CONTENT_WIDTH - (1 * inch if indent else 0)

                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if (
                        canvas.stringWidth(
                            test_line, self.default_font, self.CONTENT_FONT_SIZE
                        )
                        <= line_width_limit
                    ):
                        current_line = test_line
                    else:
                        if current_line:
                            canvas.drawString(x_pos, y_pos, current_line)
                            y_pos -= self.LINE_HEIGHT_NORMAL

                        current_line = word
                        while (
                            canvas.stringWidth(
                                current_line, self.default_font, self.CONTENT_FONT_SIZE
                            )
                            > line_width_limit
                        ):

                            for i in range(len(current_line), 0, -1):
                                if (
                                    canvas.stringWidth(
                                        current_line[:i],
                                        self.default_font,
                                        self.CONTENT_FONT_SIZE,
                                    )
                                    <= line_width_limit
                                ):
                                    canvas.drawString(x_pos, y_pos, current_line[:i])
                                    y_pos -= self.LINE_HEIGHT_NORMAL
                                    current_line = current_line[i:]
                                    break
                            if not current_line:
                                break

                if current_line:
                    canvas.drawString(x_pos, y_pos, current_line)
                    y_pos -= self.LINE_HEIGHT_NORMAL
        else:
            y_pos -= self.LINE_HEIGHT_NORMAL
        return y_pos

    def _draw_footer(self, canvas):
        y_pos = self.MARGIN_BOTTOM + self.LINE_HEIGHT_NORMAL * 2  # Position from bottom
        canvas.setFont(self.default_font, self.CONTENT_FONT_SIZE)

        date_str = f"报告生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canvas.drawString(self.MARGIN_LEFT, y_pos, "报告医生: 智能RAG问诊机器人")

        date_width = canvas.stringWidth(
            date_str, self.default_font, self.CONTENT_FONT_SIZE
        )
        canvas.drawString(
            self.PAGE_WIDTH - self.MARGIN_RIGHT - date_width, y_pos, date_str
        )



    def generate_report(self, data, filename="diagnostics_report.pdf"):
        file_path = os.path.join(self.script_path, '../resource/tmp')
        c = canvas.Canvas(os.path.join(file_path, filename), pagesize=A4)

        y_cursor = self._draw_logo(
            c, self.MARGIN_LEFT, self.PAGE_HEIGHT - self.MARGIN_TOP + (0.25 * inch)
        )


        y_cursor = self._draw_header(c, "个人健康报告")

        logo_bottom_y = (
            self.PAGE_HEIGHT - self.MARGIN_TOP - (0.75 * inch) - self.ITEM_SPACING
        )
        y_cursor = min(y_cursor, logo_bottom_y)


        if "一般项目" in data and isinstance(data["一般项目"], dict):
            y_cursor = self._draw_section_title(c, "一、一般项目", y_cursor)
            y_cursor = self._draw_key_value_pairs(c, data["一般项目"], y_cursor)
            y_cursor -= self.SECTION_SPACING  # Space after section
        else:
            print("警告: '一般项目' 数据缺失或格式不正确。")

        y_cursor = self._draw_section_title(c, "二、主诉", y_cursor)
        y_cursor = self._draw_multiline_text(c, data.get("主诉", "无"), y_cursor)
        y_cursor -= self.SECTION_SPACING

        y_cursor = self._draw_section_title(c, "三、现病史", y_cursor)
        y_cursor = self._draw_multiline_text(c, data.get("现病史", "无"), y_cursor)
        y_cursor -= self.SECTION_SPACING


        y_cursor = self._draw_section_title(c, "四、既往史", y_cursor)
        y_cursor = self._draw_multiline_text(c, data.get("既往史", "无"), y_cursor)
        y_cursor -= self.SECTION_SPACING * 2  # More space before footer


        self._draw_footer(c)

        c.save()
        print(f"报告已生成: {os.path.abspath(filename)}")
        return os.path.join(file_path, filename)


if __name__ == "__main__":
    report_data = {
        "一般项目": {
            "姓名": "张三",
            "性别": "男",
            "年龄": "42岁",  
            "血型": "A型",
            "身高": "175cm",
            "体重": "70kg",
            "联系方式": "13800138000",
            "邮箱": "zhangsan@example.com",
            "紧急联系人": "李四 电话13900139000",
            "记录时间": "2025-05-09 10:00",
        },
        "主诉": "反复咳嗽、咳痰一周，伴有轻微胸闷。",
        "现病史": "患者于一周前无明显诱因出现咳嗽，初为干咳，后转为咳白色粘痰，不易咳出。\n伴有活动后轻微胸闷，无发热、盗汗、咯血等症状。\n曾自行服用止咳糖浆，效果不佳。饮食睡眠尚可，二便正常，体重无明显变化。",
        "既往史": "高血压病史5年，口服“硝苯地平缓释片”治疗，血压控制尚可。\n否认糖尿病、心脏病史。\n否认肝炎、结核等传染病史。\n无药物过敏史，无手术外伤史。",
    }

    generator = ReportGenerator()

    # Generate the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"健康报告_{report_data['一般项目'].get('姓名', '未知姓名')}_{timestamp}.pdf"
    generator.generate_report(report_data, output_filename)

