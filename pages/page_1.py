# Contents of ~/my_app/pages/page_1.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from main_page import get_data_from_excel

st.markdown("# Page 1：新发放贷款分析 ❄️")
st.sidebar.markdown("# Page 1 ：新发放贷款分析❄️")

df1, df2 = get_data_from_excel(filename='DISTRIBUTION')
# df1, df2 = get_data_from_excel(file="./datas/1100_A_DISTRIBUTION_20220630.xlsx")
multipage = st.sidebar.radio("选择分析维度", ('整体', '金额分布', '利率分布', '本行分析'))


def select_jedf(data, issue_year, prodt_l5_up, group=None):
    if group is None:
        df_selection = data.query("issue_year == @issue_year & prodt_l5_up == @prodt_l5_up")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & issue_year == @issue_year & prodt_l5_up == @prodt_l5_up")
    issue_yearmonth_to_grade_level = pd.pivot_table(df_selection, index='issue_yearmonth',
                                                    columns='grade_level',
                                                    values='contract_amt', aggfunc=[np.sum])

    issue_yearmonth_to_grade_level = issue_yearmonth_to_grade_level.div(
        issue_yearmonth_to_grade_level.sum(axis=1),
        axis=0)
    issue_yearmonth_to_grade_level.columns = issue_yearmonth_to_grade_level.columns.droplevel(0)
    # issue_yearmonth_to_grade_level = issue_yearmonth_to_grade_level.applymap(lambda x: format(x, '.2%'))
    return issue_yearmonth_to_grade_level


def select_lldf(data, issue_year, prodt_l5_up, start_time, end_time, group=None):
    # 各等级产品加权利率
    if group is None:
        df_selection = data.query(
            "issue_year == @issue_year & issue_yearmonth>=@start_time & issue_yearmonth<=@end_time & prodt_l5_up == @prodt_l5_up")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & issue_year == @issue_year & issue_yearmonth>=@start_time & issue_yearmonth<=@end_time & prodt_l5_up == @prodt_l5_up")
    result = pd.pivot_table(df_selection, index='grade_level',
                            values=['int_contract_amt', 'contract_amt'],
                            aggfunc=[np.sum])
    result.columns = result.columns.droplevel(0)
    result.loc['北京分行'] = result.sum()
    result['rate'] = result['int_contract_amt'] / result['contract_amt']
    result['contract_amt'] = result['contract_amt'] / result.loc['北京分行']['contract_amt']
    # result['contract_amt'] = result['contract_amt'].map(lambda x: format(x, '.2%'))
    result_data = result[['rate', 'contract_amt']]
    return result_data


def Double_coordinates(df1, df2, df3, title=None):
    st.markdown('#### 数据表展示')
    df1['所属'] = '本行'
    df2['所属'] = '本组'
    df3['所属'] = '全行'
    df = pd.concat([df1, df2, df3])
    df_all = df.pivot_table(index=df.index, values=['rate', 'contract_amt'], columns='所属')
    st.table(df_all)

    st.markdown('#### 双坐标图')
    x = df3.index[0:-1]
    y1_1 = df1['contract_amt']
    y1_2 = df2['contract_amt']
    y1_3 = df3['contract_amt']

    y2_1 = df1["rate"]
    y2_2 = df2["rate"]
    y2_3 = df3["rate"]
    trace0_1 = go.Bar(x=x, y=y1_1,
                      marker=dict(color="Crimson"),
                      name="本行金额",
                      text=y1_1.apply(lambda x: format(x, '.2%')),
                      )

    trace0_2 = go.Bar(x=x, y=y1_2,
                      marker=dict(color="MediumPurple"),
                      name="本组金额",
                      text=y1_2.apply(lambda x: format(x, '.2%')),
                      )
    trace0_3 = go.Bar(x=x, y=y1_3,
                      marker=dict(color="Blue"),
                      name="全行金额",
                      text=y1_3.apply(lambda x: format(x, '.2%')),
                      )
    trace1 = go.Scatter(x=x, y=y2_1,
                        mode="markers+lines+text",
                        name="本行利率",
                        text=y2_1.round(2),
                        line=dict(color="Crimson"),
                        yaxis="y2")
    trace2 = go.Scatter(x=x, y=y2_2,
                        mode="markers+lines+text",
                        name="本组利率",
                        text=y2_2.round(2),
                        line=dict(color="MediumPurple"),
                        yaxis="y2")
    trace3 = go.Scatter(x=x, y=y2_3,
                        mode="markers+lines+text",
                        name="全行利率",
                        text=y2_3.round(2),
                        line=dict(color="Blue"),
                        yaxis="y2")

    data = [trace0_1, trace0_2, trace0_3, trace1, trace2, trace3]

    layout = go.Layout(title="{}放款金额评分等级分布及利率情况".format(title),
                       xaxis=dict(title="等级"),
                       yaxis=dict(title="金额占比"),
                       yaxis2=dict(title="利率", overlaying="y", side="right"),
                       )

    fig = go.Figure(data=data, layout=layout)

    st.plotly_chart(fig)


def select_bhdf(data, issue_year, prodt_l5_up, prodt_l5, syswd):
    df_selection = data.query(
        "issue_year == @issue_year & prodt_l5_up == @prodt_l5_up & prodt_l5 == @prodt_l5")
    result = pd.pivot_table(df_selection, index="sub_brh_name", columns='grade_level',
                            values=['int_contract_amt', 'contract_amt'], aggfunc=[np.sum])
    result.columns = result.columns.droplevel(0)
    result.loc['北京分行'] = result.sum()
    if '利率' in syswd:
        result_rate = result['int_contract_amt'] / result['contract_amt']
        st.info('各支行利率分布情况')
        st.dataframe(result_rate)
        fig1 = px.bar(result_rate,
                      x=result_rate.index,
                      y=result_rate.columns,
                      title="各支行利率分布情况"
                      )
        st.plotly_chart(fig1)
    else:
        result_rate = []
    if '金额' in syswd:
        result_contract_amt = result['contract_amt']
        result_contract_amt = result_contract_amt.div(result_contract_amt.sum(axis=1), axis=0)
        st.info('各支行金额分布情况')
        st.dataframe(result_contract_amt)
        fig2 = px.bar(result_contract_amt,
                      x=result_contract_amt.index,
                      y=result_contract_amt.columns,
                      title="各支行金额分布情况"
                      )
        st.plotly_chart(fig2)

    else:
        result_contract_amt = []
    return result_rate, result_contract_amt


if multipage == '整体':
    st.info('本行新发放贷款整体情况')
    st.dataframe(df1)

    index_select = st.selectbox(
        "产品维度选择:",
        options=['prodt_l5_up', 'prodt_l5', 'prodt_l6_up', 'prodt_no_desc'],
    )
    df1_pt = pd.pivot_table(df1, index=index_select,
                            columns='grade_level_adj',
                            values='contract_amt', aggfunc=[np.sum])
    df1_pt.columns = df1_pt.columns.droplevel(0)
    df1_pt.loc['总计'] = df1_pt.sum(axis=0).to_list()
    df1_pt_ratio = df1_pt.div(df1_pt.sum(axis=1), axis=0)
    fig = make_subplots(rows=1, cols=5, shared_yaxes=True)
    fig.add_trace(
        go.Bar(
            x=df1_pt_ratio['A'],
            y=list(df1_pt_ratio.index),
            orientation='h',
            text=df1_pt_ratio['A'].apply(lambda x: format(x, '.2%'))
        ),
        row=1,
        col=1,
    )
    fig.add_trace(go.Bar(
        x=df1_pt_ratio['B'],
        y=list(df1_pt_ratio.index),
        orientation='h',
        text=df1_pt_ratio['B'].apply(lambda x: format(x, '.2%'))

    ), row=1, col=2)
    fig.add_trace(go.Bar(
        x=df1_pt_ratio['C'],
        y=list(df1_pt_ratio.index),
        orientation='h',
        text=df1_pt_ratio['C'].apply(lambda x: format(x, '.2%'))
    ), row=1, col=3)
    fig.add_trace(go.Bar(
        x=df1_pt_ratio['D'],
        y=list(df1_pt_ratio.index),
        orientation='h',
        text=df1_pt_ratio['D'].apply(lambda x: format(x, '.2%'))
    ), row=1, col=4)
    fig.add_trace(go.Bar(
        x=df1_pt_ratio['E'],
        y=list(df1_pt_ratio.index),
        orientation='h',
        text=df1_pt_ratio['E'].apply(lambda x: format(x, '.2%'))
    ), row=1, col=5)
    fig.update_layout(height=300, width=800, title_text="{}各产品新发放贷款金额分布".format((index_select)),
                      xaxis1=dict(tickformat='2%', title='A'),
                      xaxis2=dict(tickformat='2%', title='B'),
                      xaxis3=dict(tickformat='2%', title='C'),
                      xaxis4=dict(tickformat='2%', title='D'),
                      xaxis5=dict(tickformat='2%', title='E'),
                      showlegend=False)

    st.plotly_chart(fig)

    st.info('全行新发放贷款整体情况')
    st.dataframe(df2)

if multipage == '金额分布':
    # 侧边栏
    st.sidebar.header("请在这里筛选:")
    issue_year = st.sidebar.multiselect(
        "放款年份:",
        options=df2["issue_year"].unique(),
        default=df2["issue_year"].unique()
    )

    prodt_l5_up = st.sidebar.multiselect(
        "产品类型prodt_l5_up:",
        options=df2["prodt_l5_up"].unique(),
        default=df2["prodt_l5_up"].unique()
    )

    # 分隔符
    st.markdown("""---""")

    bh_select = select_jedf(df1, issue_year, prodt_l5_up, group=None)
    bz_select = select_jedf(df2, issue_year, prodt_l5_up, group='第一组')
    qh_select = select_jedf(df2, issue_year, prodt_l5_up, group=None)

    # temp = issue_yearmonth_to_grade_level.stack().reset_index()
    # temp.columns = ['issue_yearmonth', 'grade_level_adj', 'ratio']
    fig1 = px.bar(bh_select,
                  x=bh_select.index,
                  y=bh_select.columns,
                  title="本行各等级发放贷款比例"
                  )
    fig1.update_layout(width=800,
                       height=500,  # 改变整个figure的大小
                       yaxis=dict(tickformat='2%'),
                       xaxis=dict(
                           tickangle=-45,
                           type='category')
                       )
    st.plotly_chart(fig1)

    fig2 = px.bar(bz_select,
                  x=bz_select.index,
                  y=bz_select.columns,
                  title="本组各等级发放贷款比例"
                  )
    fig2.update_layout(width=800,
                       height=500,  # 改变整个figure的大小
                       yaxis=dict(tickformat='2%'),
                       xaxis=dict(
                           tickangle=-45,
                           type='category')
                       )
    st.plotly_chart(fig2)
    fig3 = px.bar(qh_select,
                  x=qh_select.index,
                  y=qh_select.columns,
                  title="全行各等级发放贷款比例"
                  )
    fig3.update_layout(width=800,
                       height=500,  # 改变整个figure的大小
                       yaxis=dict(tickformat='2%'),
                       xaxis=dict(
                           tickangle=-45,
                           type='category')
                       )
    st.plotly_chart(fig3)
if multipage == '利率分布':
    st.sidebar.header("请在这里筛选:")
    issue_year = st.sidebar.multiselect(
        "放款年份:",
        options=df2["issue_year"].unique(),
        default=df2["issue_year"].unique()
    )

    prodt_l5_up = st.sidebar.multiselect(
        "产品类型prodt_l5_up:",
        options=df2["prodt_l5_up"].unique(),
        default=df2["prodt_l5_up"].unique()
    )
    # issue_yearmonth = st.sidebar.multiselect(
    #     "放款年月:",
    #     options=df2["issue_yearmonth"].unique(),
    #     default=sorted(df2["issue_yearmonth"].unique())
    # )
    options = sorted((df2['issue_yearmonth']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("请选择放款年月区间：",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    st.markdown('#### 分析放款区间 {} 至 {}'.format(start_time, end_time))

    # 分隔符
    st.markdown("""---""")

    bh_llselect = select_lldf(df1, issue_year, prodt_l5_up, start_time, end_time, group=None)
    bz_llselect = select_lldf(df2, issue_year, prodt_l5_up, start_time, end_time, group='第一组')
    qh_llselect = select_lldf(df2, issue_year, prodt_l5_up, start_time, end_time, group=None)

    Double_coordinates(bh_llselect, bz_llselect, qh_llselect, title=prodt_l5_up[:])

if multipage == '本行分析':
    st.sidebar.header("请在这里筛选:")
    issue_year = st.sidebar.multiselect(
        "放款年份:",
        options=df2["issue_year"].unique(),
        default=df2["issue_year"].unique()
    )

    prodt_l5_up = st.sidebar.multiselect(
        "产品类型prodt_l5_up:",
        options=df2["prodt_l5_up"].unique(),
        default=df2["prodt_l5_up"].unique()
    )
    prodt_l5 = st.sidebar.multiselect(
        "产品类型prodt_l5:",
        options=df2["prodt_l5"].unique(),
        default=df2["prodt_l5"].unique()
    )

    syswd = st.sidebar.multiselect(
        "分析维度:",
        options=['金额', '利率'],
        default=['金额', '利率']
    )
    # 分隔符
    st.markdown("""---""")
    bh_rate, bh_contract_amt = select_bhdf(df1, issue_year, prodt_l5_up, prodt_l5, syswd)

    prodt_type = st.selectbox(
        "产品维度选择:",
        options=['prodt_l5_up', 'prodt_l5', 'prodt_l6_up', 'prodt_no_desc'])
    prodt_name = st.selectbox(
        "产品选择:",
        options=df1[prodt_type].unique())
    df_selection = df1[df1[prodt_type] == prodt_name]

    issue_yearmonth_to_grade_level = pd.pivot_table(df_selection, index='issue_yearmonth',
                                                    columns='grade_level_adj',
                                                    values='contract_amt', aggfunc=[np.sum])

    issue_yearmonth_to_grade_level = issue_yearmonth_to_grade_level.div(
        issue_yearmonth_to_grade_level.sum(axis=1),
        axis=0)
    issue_yearmonth_to_grade_level.columns = issue_yearmonth_to_grade_level.columns.droplevel(0)
    fig1 = px.bar(issue_yearmonth_to_grade_level,
                  x=issue_yearmonth_to_grade_level.index,
                  y=issue_yearmonth_to_grade_level.columns,
                  title="本行{}新发放贷款各等级金额分布".format(prodt_name)
                  )
    fig1.update_layout(width=800,
                       height=500,  # 改变整个figure的大小
                       yaxis=dict(tickformat='2%'),
                       xaxis=dict(
                           tickangle=-45,
                           type='category')
                       )
    st.plotly_chart(fig1)
