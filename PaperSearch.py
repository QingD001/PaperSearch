import arxiv
from datetime import datetime, timedelta


def search_arxiv_papers(query="memory", max_results=10, start_date=None, end_date=None):
    """
    在 Arxiv 上搜索指定查询的论文。
    
    参数:
        query: 搜索关键词
        max_results: 最大结果数量
        start_date: 起始日期 (YYYY-MM-DD格式)
        end_date: 结束日期 (YYYY-MM-DD格式)
    
    返回:
        list: 论文结果列表 (arxiv.Result 对象列表)
    """
    try:
        # 如果未提供 end_date，默认为今天
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # 如果未提供 start_date，默认为 end_date 的前一天
        if not start_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # 默认搜索过去 14 天
                start_date = (end_dt - timedelta(days=14)).strftime("%Y-%m-%d")
                print(f"未指定完整日期范围，默认搜索范围: {start_date} 到 {end_date}")
            except ValueError:
                print("日期格式错误，无法计算默认起始日期。")

        # 构建时间范围查询
        original_query = query
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y%m%d0000")
            end = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y%m%d2359")
            query = f"{query} AND submittedDate:[{start} TO {end}]"
        except ValueError:
            print("日期格式错误，请使用 YYYY-MM-DD 格式。忽略日期筛选。")

        client_arxiv = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        print(f"正在搜索 Arxiv 关于 '{original_query}' 的论文...")
        
        # 返回论文结果列表
        results = list(client_arxiv.results(search))
        return results
        
    except Exception as e:
        print(f"搜索 Arxiv 时发生错误: {e}")
        return []

