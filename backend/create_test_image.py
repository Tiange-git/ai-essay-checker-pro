from PIL import Image
import os

# 创建测试图片
img = Image.new('RGB', (100, 50), color='white')
img.save('test_image.png')
print("测试图片已创建: test_image.png")
print(f"图片大小: {os.path.getsize('test_image.png')} bytes")