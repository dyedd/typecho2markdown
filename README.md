# typecho2markdown

这是一个转换 typecho 文章成 markdown 的工具

## 功能

- **翻译标题**：使用 OpenAI API 将中文标题翻译为英文缩略。
- **兼容 Hexo 等静态博客**：自己修改支持的字段即可。
- **替换图片引用**：将 Markdown 文本中的图片引用替换为直接的 URL 格式。
  - typecho 编辑器的图片引用格式是`![][1] [1]...`替换成了`![]()`
- **下载图片**：从给定的 URL 下载图片。
- **数据库集成**：从数据库中获取文章数据并处理。

## 使用方法

1. **安装依赖**

   使用以下命令安装所需的 Python 包：

   ```bash
   pip install requests pymysql openai
   ```

2. **配置数据库**

   在 `main` 函数中，修改数据库连接信息以匹配你的数据库设置。

3. **运行脚本**

   运行脚本以处理 Markdown 文本：

   ```bash
   python typecho2myblog.py
   ```

## 注意事项

- 确保你的 OpenAI API 密钥正确并可用。
  - 你可以使用各种兼容 OpenAI API 的国内外大模型！例如本例的 DeepSeek。
- 数据库中的表结构需与脚本中的查询匹配。
