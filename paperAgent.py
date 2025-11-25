# file: arxiv_agent_streamlit_one_day.py
import streamlit as st
import datetime
import arxiv  # pip install arxiv
from collections import defaultdict

def fetch_arxiv_by_day(category_list, target_date: datetime.date, max_results=200):
    """从 arXiv 抓取给定某一天提交的论文（尽可能）"""
    papers_by_cat = defaultdict(list)
    client = arxiv.Client()
    # 构造查询：使用 submittedDate 区间，从当日 00:00 到 23:59
    from_ts = target_date.strftime("%Y%m%d0000")
    to_ts   = target_date.strftime("%Y%m%d2359")
    for cat in category_list:
        query = f"cat:{cat} AND submittedDate:[{from_ts} TO {to_ts}]"
        search = arxiv.Search(
            query = query,
            max_results = max_results,
            sort_by = arxiv.SortCriterion.SubmittedDate,
            sort_order = arxiv.SortOrder.Descending,
        )
        for result in client.results(search):
            # 过滤确实是在 target_date 提交（部分可能是更新或延迟）
            if result.published.date() == target_date:
                papers_by_cat[cat].append({
                    "title": result.title,
                    "authors": [a.name for a in result.authors],
                    "published": result.published.date(),
                    "summary": result.summary,
                    "link": result.entry_id
                })
    return papers_by_cat

def main():
    st.title("arXiv 选定日期论文 Agent 展示")
    st.write("选择一个日期和类别，展示该日提交的 arXiv 论文，并按类别整理。")

    # 选择类别
    default_cats = ["cs.AI", "cs.CV", "stat.ML", "cs.CL"]
    cats = st.multiselect("选择 arXiv 类别（category）", default_cats, default=default_cats)

    # 选择单个日期
    target_date = st.date_input("选择目标日期", value=datetime.date.today() - datetime.timedelta(days=1))

    max_results = st.slider("每类别最大抓取论文数", min_value=50, max_value=500, value=200, step=50)

    if st.button("开始抓取"):
        with st.spinner(f"Fetching papers for {target_date.isoformat()} ..."):
            papers_by_cat = fetch_arxiv_by_day(cats, target_date, max_results=max_results)
        st.success("抓取完成！")

        for cat in cats:
            st.header(f"类别：{cat}")
            papers = papers_by_cat.get(cat, [])
            if not papers:
                st.write("⚠️ 该日该类别暂无新提交论文。")
            else:
                for p in papers:
                    st.subheader(p["title"])
                    st.write(f"作者：{', '.join(p['authors'])}")
                    st.write(f"提交日期：{p['published']}")
                    st.write(f"[链接]({p['link']})")
                    st.write(p["summary"])
                    st.markdown("---")

if __name__ == "__main__":
    main()