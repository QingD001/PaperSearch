from config import client_llm, MODEL_NAME


def check_relevance_with_llm(title, summary):
    """
    使用大模型判断论文是否相关
    返回: (is_relevant: bool, reason: str)
    """
    if not client_llm:
        return False, "LLM 客户端未初始化"

    prompt = f"""
    我正在做关于"人工智能系统 Memory（记忆机制）"的研究工作（例如 LLM 的上下文管理、Agent 的长期记忆、RAG、向量数据库、Neural Memory 等）。
    
    请阅读以下论文标题和摘要，判断其是否与我的工作高度相关。
    
    论文标题: {title}
    论文摘要: {summary}
    
    请严格按照以下格式返回结果：
    相关性: [是/否]
    原因: [说明相关原因，约 200 字。重点说明该方法的创新性以及未来可持续研究方面的价值。如果认为不相关，请简要说明原因]
    """

    try:
        response = client_llm.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个专业的 AI 科研助手，帮助筛选论文。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # 稍微提高温度以获得更丰富的分析
        )
        content = response.choices[0].message.content.strip()
        
        # 解析返回结果
        lines = content.split('\n')
        is_relevant = False
        reason = "未提供原因"
        
        # 简单的解析逻辑，可能需要根据 LLM 的实际输出微调
        reason_lines = []
        capture_reason = False
        
        for line in lines:
            if line.startswith("相关性"):
                if "是" in line:
                    is_relevant = True
            elif line.startswith("原因"):
                capture_reason = True
                cleaned_line = line.replace("原因:", "").replace("原因：", "").strip()
                if cleaned_line:
                    reason_lines.append(cleaned_line)
            elif capture_reason:
                reason_lines.append(line)
        
        if reason_lines:
            reason = "\n".join(reason_lines).strip()
        else:
            # 如果没抓取到"原因"标签后的内容，可能整个 content 就是原因（如果不相关）
            # 或者尝试从 content 中提取
            pass 

        # 如果解析失败但 LLM 说相关，就把整个 content 作为原因备选
        if is_relevant and reason == "未提供原因":
            reason = content

        return is_relevant, reason

    except Exception as e:
        print(f"LLM 调用出错: {e}")
        return False, f"LLM 调用出错: {e}"

