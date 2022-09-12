# Contents of ~/my_app/pages/page_3.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

from pages.page_2 import aggrid_df

st.markdown("# Page 3:C_M1分析 🎉")
st.sidebar.markdown("# Page 3:C_M1分析 🎉")
from main_page import get_data_from_excel

df1, df2 = get_data_from_excel(filename="B_ROLLRATE_1M", )
multipage = st.sidebar.radio("选择分析维度", ('整体', '时间维度', '产品维度', '本行分析'))


def select_sjdf(data, prodt_l5_up=None, prodt_l5=None, LOANSTATUS=None, group=None, index_=None):
    indexs = ['REPORT_DT']
    if index_ is not None:
        indexs.append(index_)
    sql = "DELQ_hx==0"
    if prodt_l5_up is not None:
        sql = sql + " & prodt_l5_up == @prodt_l5_up"
    if prodt_l5 is not None:
        sql = sql + " & prodt_l5 == @prodt_l5"
    if LOANSTATUS is not None:
        sql = sql + " & LOANSTATUS == @LOANSTATUS"
    if group is not None:
        sql = sql + " & brh_group_2022 == @group"
    df_selection = data.query(sql)
    # if group is None:
    #
    #     df_selection = data.query(
    #         "DELQ_hx==0 & prodt_l5_up == @prodt_l5_up & prodt_l5 == @prodt_l5 & LOANSTATUS == "
    #         "@LOANSTATUS")
    # else:
    #     df_selection = data.query(
    #         "brh_group_2022 == @group & DELQ_hx==0 & prodt_l5_up == @prodt_l5_up & prodt_l5 == "
    #         "@prodt_l5 & LOANSTATUS == @LOANSTATUS")
    result_data = pd.pivot_table(df_selection,
                                 index=indexs,
                                 columns=['DELQ_hx_n1'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    c_m1_data = result_data.div(result_data.sum(axis=1), axis=0)[[1]]
    c_m1_data.columns = ['C-M1']

    return c_m1_data


def select_cpdf(data, start_time, end_time, prodt_select, LOANSTATUS, group=None):
    # 各产品不良分析
    if group is None:
        df_selection = data.query(
            "REPORT_DT >= @start_time & REPORT_DT <= @end_time & LOANSTATUS == @LOANSTATUS & DELQ_hx==0")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & REPORT_DT >= @start_time & REPORT_DT <= @end_time & LOANSTATUS == @LOANSTATUS & DELQ_hx==0")
    result_data = pd.pivot_table(df_selection,
                                 index=prodt_select,
                                 columns=['DELQ_hx_n1'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    c_m1_data = result_data.div(result_data.sum(axis=1), axis=0)[[1]]
    c_m1_data.columns = ['C-M1']
    return c_m1_data


def select_bhdf(data, start_time, end_time, LOANSTATUS, index_select):
    # 各支行不良分析
    df_selection = data.query("DELQ_hx == 0 & REPORT_DT >= @start_time & REPORT_DT <= @end_time "
                              "& LOANSTATUS == @LOANSTATUS")
    # 余额、不良
    if index_select == 'sub_brh_name':
        select_pt_name = st.selectbox("选择产品分析",
                                      ['全部', '个人非房消费贷款', '个人经营性贷款', '个人住房消费贷款'])
        if select_pt_name == '全部':
            pass
        else:
            df_selection = df_selection[df_selection['prodt_l5_up'] == select_pt_name]
        pg_title = "各支行{}C-M1滚动率".format(select_pt_name)
    else:
        pg_title = "{}C-M1滚动率".format(index_select)
    result_data = pd.pivot_table(df_selection,
                                 index=index_select,
                                 columns=['DELQ_hx_n1'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    c_m1_data = result_data.div(result_data.sum(axis=1), axis=0)[[1]]
    c_m1_data.columns = ['C-M1']
    ye_data = result_data[[1]]
    ye_data.columns = ['贷款余额']
    bf_sysdata = pd.concat([c_m1_data, ye_data], axis=1)

    bf_sysdata.reset_index(inplace=True)
    aggrid_df(bf_sysdata)
    fig1 = go.Bar(x=bf_sysdata[index_select],
                  y=bf_sysdata['贷款余额'],
                  name='贷款余额')

    fig2 = go.Scatter(x=bf_sysdata[index_select],
                      y=bf_sysdata['C-M1'],
                      mode='lines+markers+text',
                      text=bf_sysdata['C-M1'].apply(lambda x: format(x, '.2%')),
                      yaxis="y2",
                      name='C-M1')
    datas = [fig1, fig2]
    layout = go.Layout(title=pg_title,
                       xaxis=dict(tickangle=-45),
                       yaxis=dict(title="贷款余额"),
                       yaxis2=dict(title="C-M1", overlaying="y", side="right", tickformat='2%'),
                       )
    fig = go.Figure(data=datas, layout=layout)
    st.plotly_chart(fig)

    ## 下钻分析 ['sub_brh_name', 'prodt_l5_up', 'prodt_l5', 'prodt_l6_up'],
    sub_brh_name = st.selectbox("下钻支行分析",
                                data["sub_brh_name"].unique())
    cp_type = st.selectbox("选择产品等级",
                           ('prodt_l5', 'prodt_l6_up', 'prodt_l5_up'))
    df2_selection = df_selection.query("sub_brh_name == @sub_brh_name")
    result_data2 = pd.pivot_table(df2_selection,
                                  index=cp_type,
                                  columns=['DELQ_hx_n1'],
                                  values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                  aggfunc=[np.sum])
    result_data2.columns = result_data2.columns.droplevel([0, 1])
    c_m1_data_2 = result_data2.div(result_data2.sum(axis=1), axis=0)[[1]]
    c_m1_data_2.columns = ['C-M1']
    ye_data_2 = result_data2[[1]]
    ye_data_2.columns = ['贷款余额']
    bf_sysdata_2 = pd.concat([c_m1_data_2, ye_data_2], axis=1)
    bf_sysdata_2.reset_index(inplace=True)
    bf_sysdata_2.fillna(0, inplace=True)
    datas_2 = [go.Bar(x=bf_sysdata_2[cp_type],
                      y=bf_sysdata_2['贷款余额'],
                      text=bf_sysdata_2['贷款余额'].round(),
                      textposition='outside',
                      name='贷款余额'),
               go.Scatter(x=bf_sysdata_2[cp_type],
                          y=bf_sysdata_2['C-M1'],
                          mode='lines+markers+text',
                          text=bf_sysdata_2['C-M1'].apply(lambda x: format(x, '.2%')),
                          line=dict(color="Crimson"),
                          yaxis="y2",
                          name='C-M1')]
    layout2 = go.Layout(title="{} {} 维度C-M1图".format(sub_brh_name, cp_type),
                        xaxis=dict(title=cp_type),
                        yaxis=dict(title="贷款余额"),
                        yaxis2=dict(title="C-M1", overlaying="y", side="right",tickformat='2%'),
                        )
    fig2 = go.Figure(data=datas_2, layout=layout2)
    st.plotly_chart(fig2)


if multipage == '整体':
    st.info('本行C_M1整体数据')
    st.dataframe(df1)
    st.info('全行C_M1整体数据')
    st.dataframe(df2)

if multipage == '时间维度':
    # 侧边栏
    st.sidebar.header("请在这里筛选:")
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
    LOANSTATUS = st.sidebar.multiselect(
        "贷款状态:",
        options=df2["LOANSTATUS"].unique(),
        default=['FS01']
    )
    # 分隔符
    st.markdown("""---""")

    bh_select = select_sjdf(df1, prodt_l5_up, prodt_l5, LOANSTATUS, group=None)
    st.info('本行 {} C_M1滚动率整体情况'.format(prodt_l5_up))
    st.table(bh_select)
    bz_select = select_sjdf(df2, prodt_l5_up, prodt_l5, LOANSTATUS, group='第一组')
    st.info('本组 {} C_M1滚动率整体情况'.format(prodt_l5_up))
    st.table(bz_select)
    qh_select = select_sjdf(df2, prodt_l5_up, prodt_l5, LOANSTATUS, group=None)
    st.info('全行 {} C_M1滚动率整体情况'.format(prodt_l5_up))
    st.table(qh_select)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bh_select.index,
                             y=bh_select['C-M1'],
                             mode='lines+markers+text',
                             text=bh_select['C-M1'].apply(lambda x: format(x, '.2%')),
                             line=dict(color="Crimson"),
                             name='本行'))
    fig.add_trace(go.Scatter(x=bz_select.index,
                             y=bz_select['C-M1'],
                             mode='lines+markers+text',
                             text=bz_select['C-M1'].apply(lambda x: format(x, '.2%')),
                             line=dict(color="MediumPurple"),
                             name='本组'))
    fig.add_trace(go.Scatter(x=qh_select.index,
                             y=qh_select['C-M1'],
                             mode='lines+markers+text',
                             text=qh_select['C-M1'].apply(lambda x: format(x, '.2%')),
                             line=dict(color="Blue"),
                             name='全行'))
    fig.update_layout(width=800,
                      height=500,  # 改变整个figure的大小
                      title_text="产品 {} 全行、本组、本行C-M1滚动率".format(prodt_l5_up),
                      xaxis=dict(tickformat="%Y-%m"),
                      yaxis=dict(tickformat='2%'),
                      )
    st.plotly_chart(fig)
    # 对全行、本组及本行个人非房消费、个人经营性贷款及个人住房消费贷款业务C-M1滚动率进行展示
    # 分隔符
    st.markdown("""---""")
    st.markdown("### 对全行、本组及本行个人非房消费、个人经营性贷款及个人住房消费贷款业务C-M1滚动率进行展示")
    select_name = st.selectbox("选择分析标的",
                               ['本行', '全行', '本组'])
    if select_name == '本行':
        select_bh = select_sjdf(df1, index_='prodt_l5_up')
    elif select_name == '本组':
        select_bh = select_sjdf(df2, group='第一组', index_='prodt_l5_up')
    else:
        select_bh = select_sjdf(df2, index_='prodt_l5_up')
    select_bh.reset_index(inplace=True)
    fig = px.line(select_bh,
                  x='REPORT_DT',
                  y='C-M1',
                  text=select_bh['C-M1'].apply(lambda x: format(x, '.2%')),
                  color='prodt_l5_up',
                  title="个人非房消费、个人经营性贷款及个人住房消费贷款业务C-M1滚动率"
                  )
    fig.update_layout(height=500, width=800,
                      yaxis=dict(tickformat='2%'),
                      xaxis=dict(
                          tickangle=-45,
                          type='category')
                      )
    st.plotly_chart(fig)

if multipage == '产品维度':
    # 侧边栏
    st.sidebar.header("请在这里筛选:")
    options = sorted((df2['REPORT_DT']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("请选择报告年月区间：",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    prodt_select = st.sidebar.selectbox('选择产品分类的标准', ('prodt_l5_up', 'prodt_l5'))
    st.markdown('#### 报告区间 {} 至 {} 各产品C-M1分析'.format(start_time, end_time))
    LOANSTATUS = st.sidebar.multiselect(
        "贷款状态:",
        options=df2["LOANSTATUS"].unique(),
        default=['FS01']
    )
    # 分隔符
    st.markdown("""---""")

    bh_select = select_cpdf(df1, start_time, end_time, prodt_select, LOANSTATUS, group=None)
    st.info('本行 {} 至 {} 各产品C_M1整体情况'.format(start_time, end_time))
    st.table(bh_select)
    bz_select = select_cpdf(df2, start_time, end_time, prodt_select, LOANSTATUS, group='第一组')
    st.info('本组 {} 至 {} 各产品C_M1整体情况'.format(start_time, end_time))
    st.table(bz_select)
    qh_select = select_cpdf(df2, start_time, end_time, prodt_select, LOANSTATUS, group=None)
    st.info('全行 {} 至 {} 各产品C_M1整体情况'.format(start_time, end_time))
    st.table(qh_select)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=bh_select.index,
                         y=bh_select['C-M1'],
                         text=bh_select['C-M1'].apply(lambda x: format(x, '.2%')),
                         textposition='outside',
                         name='本行'))
    fig.add_trace(go.Bar(x=bz_select.index,
                         y=bz_select['C-M1'],
                         text=bz_select['C-M1'].apply(lambda x: format(x, '.2%')),
                         textposition='outside',
                         name='本组'))
    fig.add_trace(go.Bar(x=qh_select.index,
                         y=qh_select['C-M1'],
                         text=qh_select['C-M1'].apply(lambda x: format(x, '.2%')),
                         textposition='outside',
                         name='全行'))
    fig.update_layout(width=800,
                      height=500,  # 改变整个figure的大小
                      title_text=' {} 至 {} 各产品C_M1整体情况'.format(start_time, end_time),
                      xaxis=dict(tickformat="%Y-%m"),
                      yaxis=dict(title="C-M1", overlaying="y", tickformat='2%'),
                      )
    st.plotly_chart(fig)
if multipage == '本行分析':
    # 机构、产品、维度分析
    st.sidebar.header("请在这里筛选:")
    options = sorted((df1['REPORT_DT']).tolist())
    (start_time, end_time) = st.sidebar.select_slider("请选择报告年月区间：",
                                                      options=options,
                                                      value=(min(options), max(options)),
                                                      )
    LOANSTATUS = st.sidebar.multiselect(
        "贷款状态:",
        options=df1["LOANSTATUS"].unique(),
        default=['FS01']
    )
    index_select = st.sidebar.selectbox(
        "维度选择:",
        options=['sub_brh_name', 'prodt_l5_up', 'prodt_l5', 'prodt_l6_up'],
    )

    st.markdown('#### 报告区间 {} 至 {} 各{} C-M1分析'.format(start_time, end_time, index_select))
    bf_sysdata = select_bhdf(df1, start_time, end_time, LOANSTATUS, index_select)
