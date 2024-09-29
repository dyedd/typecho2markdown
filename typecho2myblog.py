import os
import re
import requests
import pymysql
from datetime import datetime


from openai import OpenAI

client = OpenAI(api_key="sk", base_url="https://api.deepseek.com")

# 将中文标题翻译为英文缩略
def translate_title_to_english(chinese_title):
    prompt = f"""
你是一个专业的翻译助手，擅长将中文标题转换为简洁且合适的英文缩略。请根据下面的中文标题，提供一个准确且简明的英文缩略形式。请确保缩略语保留标题的核心含义，并适合用作文件名或标签。
示例：
中文标题: "Github Benefits 学生认证/学生包 新版申请指南"
英文缩略: "github-benefits-2024"
注意：
1. 你只需要返回英文字符串，不附带带双引号或者是英文缩略的文字
任务:
中文标题: "{chinese_title}"

"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content.strip()


# 下载图片
def download_image(url, path, title):
    try:
        response = requests.get(url)
        response.raise_for_status()
        filename = os.path.join(path, os.path.basename(url))
        with open(filename, 'wb') as f:
            f.write(response.content)
    except requests.RequestException as e:
        print(f"IN {title}, Failed to download {url}: {e}")


# 替换 Markdown 中的图片引用
def replace_markdown_images(text):
    # 查找所有的图片引用
    ref_pattern = re.compile(r'!\[.*?\]\[(\d+)\]')
    url_pattern = re.compile(r'\[(\d+)\]:\s*(\S+)')

    # 创建一个字典来存储编号和 URL 的映射
    url_dict = {}
    for match in url_pattern.finditer(text):
        number = match.group(1)
        url = match.group(2)
        # 移除 URL 中的参数部分
        clean_url = re.sub(r'#.*$', '', url)
        url_dict[number] = clean_url

    # 替换旧的语法为新的语法
    def replacer(match):
        ref_number = match.group(1)
        url = url_dict.get(ref_number, '')
        return f'![Image]({url})'

    # 替换图片引用
    new_text = ref_pattern.sub(replacer, text)

    # 移除 URL 映射部分
    new_text = url_pattern.sub('', new_text)

    return new_text.strip()

# 从 URL 中提取文件名
def extract_filename_from_url(url):
    # 移除 URL 中的参数部分
    clean_url = re.sub(r'#.*$', '', url)
    # 提取文件名
    file_name = clean_url.split('/')[-1]
    return file_name
    
# 将 URL 替换为文件名
def replace_urls_with_filenames(text):
    # 匹配 Markdown 图片语法的正则表达式
    pattern = re.compile(r'(!\[.*?\]\()(\S+)(\))')
    
    # 替换 URL 为文件名
    def replacer(match):
        url = match.group(2)
        file_name = extract_filename_from_url(url)
        return f'{match.group(1)}{file_name}{match.group(3)}'

    new_text = pattern.sub(replacer, text)
    return new_text


def create_data(db):
    # 创建文章
    with db.cursor() as cursor:
        cursor.execute("SELECT cid, title, slug, text, created FROM typecho_contents WHERE type='post'")
        entries = cursor.fetchall()
        for e in entries:
            title = translate_title_to_english(e['title'])
            content = e['text'] or ''  # 如果 text 是 None，则使用空字符串
            content = content.replace('<!--markdown-->', '')
            content = replace_markdown_images(content)
            tags = []
            # category = ""
            cursor.execute(
                "SELECT type, name, slug FROM typecho_relationships ts, typecho_metas tm WHERE tm.mid = ts.mid AND ts.cid = %s",
                (e['cid'],)
            )
            metas = cursor.fetchall()
            for m in metas:
                if m['type'] == 'tag':
                    tags.append(m['name'])
                # if m['type'] == 'category':
                #     category = m['slug']
            path = f'data/{title}'
            if not os.path.exists(path):
                os.makedirs(path)

            image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
            for url in image_urls:
                download_image(url, path, title)
            content =replace_urls_with_filenames(content)    
            with open(f'{path}/README.md', 'w', encoding='utf-8') as f:
                f.write(f"title: {title}\n")
                f.write(f"date: {datetime.fromtimestamp(e['created']).strftime('%Y-%m-%d %H:%M:%S')}\n")
                # f.write(f"categories: {category}\n")
                f.write(f"tags: [{','.join(tags)}]\n")
                f.write("---\n")
                f.write(content)


def main():
    # 把数据库相关信息改成自己的，默认localhost（和数据库同机的话不需要修改）
    db = pymysql.connect(
        host="localhost",
        user="dyedd",
        password="E4L",
        database="dyedd",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        create_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
