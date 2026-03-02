import datetime as dt
from collections import defaultdict
from zoneinfo import ZoneInfo

import arxiv
import streamlit as st


BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def _beijing_today():
    return dt.datetime.now(BEIJING_TZ).date()


def _day_window_utc(target_date: dt.date):
    start_local = dt.datetime.combine(target_date, dt.time.min, tzinfo=BEIJING_TZ)
    end_local = dt.datetime.combine(target_date, dt.time.max, tzinfo=BEIJING_TZ)
    start_utc = start_local.astimezone(dt.timezone.utc)
    end_utc = end_local.astimezone(dt.timezone.utc)
    return start_utc, end_utc


def fetch_arxiv_for_today(categories, max_results=200):
    target_date = _beijing_today()
    start_utc, end_utc = _day_window_utc(target_date)
    from_ts = start_utc.strftime("%Y%m%d%H%M")
    to_ts = end_utc.strftime("%Y%m%d%H%M")

    papers_by_cat = defaultdict(list)
    client = arxiv.Client()

    for cat in categories:
        query = f"cat:{cat} AND submittedDate:[{from_ts} TO {to_ts}]"
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        for result in client.results(search):
            papers_by_cat[cat].append(
                {
                    "title": result.title.strip(),
                    "authors": ", ".join(a.name for a in result.authors),
                    "published": result.published,
                    "url": result.entry_id,
                    "summary": (result.summary or "").strip(),
                }
            )
    return target_date, papers_by_cat


def run_arxiv_today_app():
    st.title("📚 今日 arXiv 论文")
    st.markdown("点击按钮，一键获取今天（北京时间）发布的 arXiv 论文。")

    default_cats = ["cs.AI", "cs.CV", "cs.CL", "cs.LG", "stat.ML"]
    categories = st.multiselect("选择类别", default_cats, default=default_cats)
    max_results = st.slider("每个类别最大抓取数", min_value=50, max_value=500, value=200, step=50)

    if st.button("一键获取今日论文", type="primary"):
        if not categories:
            st.warning("请至少选择一个类别。")
            return
        try:
            with st.spinner("正在抓取今日论文..."):
                target_date, papers_by_cat = fetch_arxiv_for_today(
                    categories=categories, max_results=max_results
                )

            st.success(f"抓取完成：{target_date.isoformat()}（北京时间）")
            for cat in categories:
                papers = papers_by_cat.get(cat, [])
                st.subheader(f"{cat}（{len(papers)} 篇）")
                if not papers:
                    st.info("该类别今天暂无结果。")
                    continue
                for p in papers:
                    st.markdown(f"**{p['title']}**")
                    st.caption(f"作者：{p['authors']} | 发布时间(UTC)：{p['published']:%Y-%m-%d %H:%M}")
                    st.markdown(f"[论文链接]({p['url']})")
                    if p["summary"]:
                        st.write(p["summary"])
                    st.markdown("---")
        except Exception as exc:
            st.error(f"抓取失败：{exc}")
