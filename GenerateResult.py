import os
import re
from datetime import datetime


def sanitize_filename(title: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', '_', title)
    if len(filename) > 200:
        filename = filename[:200]
    return filename.strip()


def generate_title_anchor(title: str) -> str:
    anchor = title.lower()
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[-\s]+', '-', anchor)
    return anchor.strip('-')


def generate_markdown_content(paper_result, is_relevant: bool, reason: str):
    anchor = generate_title_anchor(paper_result.title)
    md_content = []
    md_content.append(f"# {paper_result.title}\n")
    md_content.append(f"**作者**: {', '.join(author.name for author in paper_result.authors)}\n")
    md_content.append(f"**发表日期**: {paper_result.published.strftime('%Y-%m-%d')}\n")
    md_content.append(f"**Arxiv 链接**: [{paper_result.entry_id}]({paper_result.entry_id})\n")
    if is_relevant:
        md_content.append("\n## 推荐原因\n")
    else:
        md_content.append("\n## 筛选理由\n")
    md_content.append(f"{reason}\n")
    md_content.append("\n## 原始摘要\n")
    md_content.append(f"> {paper_result.summary.replace(chr(10), ' ')}\n")
    return anchor, "\n".join(md_content)


def save_and_package_results(paper_results, relevance_results, date_str: str):
    """
    将结果导出为两个文件（PDF 优先，回退为 Markdown）：
      - results/relevant_{date_str}.pdf 或 .md
      - results/irrelevant_{date_str}.pdf 或 .md

    返回 (count_relevant, count_irrelevant)
    """
    os.makedirs("results", exist_ok=True)

    relevant_papers = []
    irrelevant_papers = []

    for i, (paper_result, (is_relevant, reason)) in enumerate(zip(paper_results, relevance_results), 1):
        print(f"正在分析第 {i} 篇: {paper_result.title[:50]}...")
        authors = ', '.join(a.name for a in paper_result.authors)
        summary = (paper_result.summary or '').replace('\n', ' ').strip()
        # 将推荐理由限制为大约 100 字（按空格切分为词）
        def truncate_words(text, max_words=100):
            parts = text.split()
            if len(parts) <= max_words:
                return text
            return ' '.join(parts[:max_words]) + '...'

        short_reason = truncate_words(reason or '', 100)

        entry = {
            'title': paper_result.title,
            'link': paper_result.entry_id,
            'authors': authors,
            'summary': summary,
            'reason': short_reason,
        }

        if is_relevant:
            relevant_papers.append(entry)
        else:
            irrelevant_papers.append(entry)

    # 输出到同一个合并的 Markdown 文件（不按日期分割）
    out_file = os.path.join('results', 'all_results.md')

    # 读取已有内容，拆分为两个部分（Relevant / Irrelevant）
    existing_relevant = ''
    existing_irrelevant = ''
    if os.path.exists(out_file):
        with open(out_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # 尝试查找两个部分的分界
        idx_rel = content.find('\n# Irrelevant')
        if idx_rel == -1:
            # 没有 Irrelevant 标记，整个文件作为 existing_relevant
            # 但如果存在 '# Irrelevant' 没有换行的情况也处理
            idx_rel = content.find('# Irrelevant')
        if idx_rel != -1:
            # 找到 Irrelevant 的位置
            # 找到 '# Relevant' 的位置
            idx_r = content.find('# Relevant')
            if idx_r == -1:
                # 整个上半部分为 existing_relevant
                existing_relevant = content[:idx_rel].strip()
            else:
                existing_relevant = content[idx_r:idx_rel].strip()
            existing_irrelevant = content[idx_rel:].strip()
        else:
            # 未找到 Irrelevant，查找 Relevant
            idx_r = content.find('# Relevant')
            if idx_r != -1:
                existing_relevant = content[idx_r:].strip()
            else:
                # 文件存在但没有结构，保留全部作为 existing_relevant
                existing_relevant = content.strip()

    # 构建新条目文本
    def build_entries(entries, is_relevant=True):
        parts = []
        for p in entries:
            parts.append(f"## {p['title']}\n\n")
            parts.append(f"- ArXiv: {p['link']}\n")
            parts.append(f"- 作者: {p['authors']}\n")
            parts.append(f"- 概括: {p['summary']}\n")
            parts.append(f"- {'推荐原因' if is_relevant else '筛选理由'}: {p['reason']}\n\n")
        return ''.join(parts)

    new_relevant_text = build_entries(relevant_papers, True)
    new_irrelevant_text = build_entries(irrelevant_papers, False)

    # 合并并写回文件：保证文件包含两个一级标题
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('# Relevant\n\n')
        if existing_relevant:
            # 如果 existing_relevant 包含标题，移除重复标题
            rel = existing_relevant
            if rel.startswith('# Relevant'):
                rel = rel[len('# Relevant'):].strip()
            f.write(rel + '\n\n')
        if new_relevant_text:
            f.write(new_relevant_text)
        f.write('\n---\n\n')

        f.write('# Irrelevant\n\n')
        if existing_irrelevant:
            ir = existing_irrelevant
            if ir.startswith('# Irrelevant'):
                ir = ir[len('# Irrelevant'):].strip()
            f.write(ir + '\n\n')
        if new_irrelevant_text:
            f.write(new_irrelevant_text)

    count_relevant = len(relevant_papers)
    count_irrelevant = len(irrelevant_papers)
    print(f"所有结果已追加/保存至: {out_file}")
    print(f"   - 本次相关论文: {count_relevant} 篇")
    print(f"   - 本次不相关论文: {count_irrelevant} 篇")

    return count_relevant, count_irrelevant
