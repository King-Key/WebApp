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


def fetch_arxiv_for_date(categories, target_date: dt.date, max_results=200):
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
    st.title("📚 arXiv 当天最新论文")
    st.markdown("选择日期后，一键获取该日期（北京时间）提交的最新 arXiv 论文。")

    default_cats = ["cs.AI", "cs.CV", "cs.CL", "cs.LG", "stat.ML"]
    categories = st.multiselect("选择类别", default_cats, default=default_cats)
    target_date = st.date_input("选择日期（北京时间）", value=_beijing_today(), max_value=_beijing_today())
    max_results = st.slider("每个类别最大抓取数", min_value=50, max_value=500, value=200, step=50)

    if st.button("获取所选日期论文", type="primary"):
        if not categories:
            st.warning("请至少选择一个类别。")
            return
        try:
            with st.spinner("正在抓取论文..."):
                _, papers_by_cat = fetch_arxiv_for_date(categories=categories, target_date=target_date, max_results=max_results)

            st.success(f"抓取完成：{target_date.isoformat()}（北京时间）")
            for cat in categories:
                papers = papers_by_cat.get(cat, [])
                papers.sort(key=lambda x: x["published"], reverse=True)
                st.subheader(f"{cat}（{len(papers)} 篇）")
                if not papers:
                    st.info("该类别在所选日期暂无结果。")
                    continue
                for p in papers:
                    published_beijing = p["published"].astimezone(BEIJING_TZ)
                    st.markdown(f"**{p['title']}**")
                    st.caption(
                        f"作者：{p['authors']} | 提交时间(北京时间)：{published_beijing:%Y-%m-%d %H:%M}"
                    )
                    st.markdown(f"[论文链接]({p['url']})")
                    if p["summary"]:
                        st.write(p["summary"])
                    st.markdown("---")
        except Exception as exc:
            st.error(f"抓取失败：{exc}")
