import schedule
import time
from datetime import datetime, timedelta
from PaperSearch import search_arxiv_papers
from PaperJudge import check_relevance_with_llm
from GenerateResult import save_and_package_results


def search_arxiv(query="memory", max_results=10, start_date=None, end_date=None):
    """
    在 Arxiv 上搜索指定查询的论文，判断相关性，并生成结果。
    整合了搜索、判断、生成结果三个模块。
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

        # 使用日期作为压缩包名称
        date_str = start_date if start_date else datetime.now().strftime('%Y-%m-%d')
        
        print(f"--- 正在处理日期: {date_str} ---")
        
        # 1. 搜索论文
        paper_results = search_arxiv_papers(query, max_results, start_date, end_date)
        
        if not paper_results:
            print(f"日期 {date_str} 未找到任何论文。")
            return
        
        # 2. 判断每篇论文的相关性
        relevance_results = []
        for result in paper_results:
            is_relevant, reason = check_relevance_with_llm(result.title, result.summary)
            relevance_results.append((is_relevant, reason))
        
        # 3. 生成结果并打包
        count_relevant, count_irrelevant = save_and_package_results(
            paper_results, relevance_results, date_str
        )
        
        # 汇总信息
        total_processed = len(paper_results)
        summary_msg = f"完成日期 {date_str} 的分析: 共 {total_processed} 篇 | ✅ 相关: {count_relevant} | ❌ 不相关: {count_irrelevant}"
        print(summary_msg)
        
    except Exception as e:
        print(f"搜索 Arxiv 时发生错误: {e}")


def run_weekly_task():
    """
    每周例行执行的任务：回顾过去 14 天的所有论文
    """
    print(f"\n🚀 [Agent 任务触发] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("开始按天遍历搜索过去 14 天的论文...")
    
    today = datetime.now()
    for i in range(14):
        # 计算当天的日期
        current_date = today - timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # 搜索当天
        search_arxiv(
            query="memory", 
            max_results=50, 
            start_date=date_str, 
            end_date=date_str
        )
    print(f"\n✨ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 每周任务执行完毕，继续监听环境...")


if __name__ == "__main__":
    # 设定调度任务：每周一 00:00
    schedule.every().monday.at("00:00").do(run_weekly_task)

    print("="*50)
    print(f"🤖 PaperAgent 智能体模式已启动")
    print(f"📅 运行模式: 每周一 00:00 自动追更 Arxiv 论文")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    print("Agent 正在后台巡逻，请保持程序运行...")

    # 初次启动时，建议用户手动确认是否需要立即跑一次
    # 如果想立即运行测试，可以取消下面这行的注释
    # run_weekly_task()

    heartbeat_count = 0
    while True:
        # 运行所有到期的任务
        schedule.run_pending()
        
        # 每秒循环一次，减少 CPU 压力
        time.sleep(1)
        
        # 每小时打印一次心跳信息
        heartbeat_count += 1
        if heartbeat_count >= 3600:
            print(f"💓 [Heartbeat] {datetime.now().strftime('%H:%M:%S')} - Agent 运行正常，持续感知环境中...")
            heartbeat_count = 0

