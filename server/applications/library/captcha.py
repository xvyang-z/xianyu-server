from PIL import Image, ImageDraw, ImageFont
import random
import io
from hashlib import md5
from exts import redis
from setting import RESOURCE_DIR


def generate_captcha(width=140, height=50) -> tuple[bytes, str]:
    letters = '0123456789'
    captcha_text = ''.join(random.choice(letters) for _ in range(4))
    img = Image.new('RGB', (width, height), color=(255, 255, 255))

    d = ImageDraw.Draw(img)

    # 加载字体
    font_path = RESOURCE_DIR / "monaco.ttf"
    font_size = int(height * 0.6)
    font = ImageFont.truetype(font=font_path, size=font_size)

    # 计算每个字符的平均宽度并据此调整间距
    avg_char_width = (width - 20) / len(captcha_text)  # 留出边缘空间
    offset = 10  # 起始偏移量

    # 随机颜色字母和边界框
    for char in captcha_text:
        # 随机y轴位置以增加复杂性，确保字符在垂直方向上不会超出图片边界
        y = random.randint(0, max(0, height - font_size))
        fill_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        d.text((offset, y), char, fill=fill_color, font=font)
        offset += avg_char_width  # 根据平均字符宽度调整下一个字符的位置

    # 添加干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        d.line((x1, y1, x2, y2), fill="black", width=1)

    captcha_id = md5(captcha_text.encode()).hexdigest()
    redis.set(captcha_id, captcha_text, ex=180)  # 存储验证码，有效期为180秒

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue(), captcha_id
