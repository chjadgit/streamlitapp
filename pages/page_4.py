# Contents of ~/my_app/pages/page_4.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from main_page import get_data_from_excel
from pages.page_2 import aggrid_df

st.markdown("# Page 3:M1_M3分析 🎉")
st.sidebar.markdown("# Page 3:M1_M3分析 🎉")


df1, df2 = get_data_from_excel(filename="B_ROLLRATE_2M")
multipage = st.sidebar.radio("选择分析维度", ('整体', '时间维度', '产品维度', '本行分析'))


def select_sjdf(data, prodt_l5_up, prodt_l5, LOANSTATUS, group=None):
    if group is None:
        df_selection = data.query(
            "DELQ_hx==1 & prodt_l5_up == @prodt_l5_up & prodt_l5 == @prodt_l5 & LOANSTATUS == "
            "@LOANSTATUS")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & DELQ_hx==1 & prodt_l5_up == @prodt_l5_up & prodt_l5 == "
            "@prodt_l5 & LOANSTATUS == @LOANSTATUS")
    result_data = pd.pivot_table(df_selection,
                                 index='REPORT_DT',
                                 columns=['DELQ_hx_n2'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    m1_m3_data = result_data.div(result_data.sum(axis=1), axis=0)[[3]]
    m1_m3_data.columns = ['M1-M3']

    return m1_m3_data


def select_cpdf(data, start_time, end_time, prodt_select, LOANSTATUS, group=None):
    # 各产品不良分析
    if group is None:
        df_selection = data.query(
            "REPORT_DT >= @start_time & REPORT_DT <= @end_time & LOANSTATUS == @LOANSTATUS & "
            "DELQ_hx==1")
    else:
        df_selection = data.query(
            "brh_group_2022 == @group & REPORT_DT >= @start_time & REPORT_DT <= @end_time & "
            "LOANSTATUS == @LOANSTATUS & DELQ_hx==1")
    result_data = pd.pivot_table(df_selection,
                                 index=prodt_select,
                                 columns=['DELQ_hx_n2'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    m1_m3_data = result_data.div(result_data.sum(axis=1), axis=0)[[3]]
    m1_m3_data.columns = ['M1-M3']
    return m1_m3_data


def select_bhdf(data, start_time, end_time, LOANSTATUS, index_select):
    # 各支行不良分析
    df_selection = data.query("DELQ_hx == 1 & REPORT_DT >= @start_time & REPORT_DT <= @end_time "
                              "& LOANSTATUS == @LOANSTATUS")
    result_data = pd.pivot_table(df_selection,
                                 index=index_select,
                                 columns=['DELQ_hx_n2'],
                                 values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                 aggfunc=[np.sum])
    result_data.columns = result_data.columns.droplevel([0, 1])
    m1_m3_data = result_data.div(result_data.sum(axis=1), axis=0)[[3]]
    m1_m3_data.columns = ['m1-m3']
    ye_data = result_data[[3]]   ##
    ye_data.columns = ['贷款余额']
    bf_sysdata = pd.concat([m1_m3_data, ye_data], axis=1)

    bf_sysdata.reset_index(inplace=True)
    aggrid_df(bf_sysdata)
    if len(index_select) == 1:
        # 余额、不良
        fig1 = go.Bar(x=bf_sysdata[index_select[0]],
                      y=bf_sysdata['贷款余额'],
                      name='贷款余额')

        fig2 = go.Scatter(x=bf_sysdata[index_select[0]],
                          y=bf_sysdata['m1-m3'],
                          mode="lines",
                          yaxis="y2",
                          name='m1-m3')
        datas = [fig1, fig2]
        layout = go.Layout(title="{} 维度m1-m3图".format(index_select[0]),
                           xaxis=dict(title=index_select[0]),
                           yaxis=dict(title="贷款余额"),
                           yaxis2=dict(title="m1-m3", overlaying="y", side="right"),
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
                                  columns=['DELQ_hx_n2'],
                                  values=['prin_balance_sum_w'],  # prin_balance_sum_n1_w
                                  aggfunc=[np.sum])
    result_data2.columns = result_data2.columns.droplevel([0, 1])
    m1_m3_data_2 = result_data2.div(result_data2.sum(axis=1), axis=0)[[3]]
    m1_m3_data_2.columns = ['m1-m3']
    ye_data_2 = result_data2[[3]]
    ye_data_2.columns = ['贷款余额']
    bf_sysdata_2 = pd.concat([m1_m3_data_2, ye_data_2], axis=1)
    bf_sysdata_2.reset_index(inplace=True)
    bf_sysdata_2.fillna(0, inplace=True)
    datas_2 = [go.Bar(x=bf_sysdata_2[cp_type],
                      y=bf_sysdata_2['贷款余额'],
                      name='贷款余额'),
               go.Scatter(x=bf_sysdata_2[cp_type],
                          y=bf_sysdata_2['m1-m3'],
                          mode="lines",
                          yaxis="y2",
                          name='m1-m3')]
    layout2 = go.Layout(title="{} {} 维度M1-M3图".format(sub_brh_name, cp_type),
                        xaxis=dict(title=cp_type),
                        yaxis=dict(title="贷款余额"),
                        yaxis2=dict(title="M1-M3", overlaying="y", side="right"),
                        )
    fig2 = go.Figure(data=datas_2, layout=layout2)
    st.plotly_chart(fig2)


if multipage == '整体':
    st.info('本行M1-M3整体数据')
    st.dataframe(df1)
    st.info('全行M1-M3整体数据')
    st.dataframe(df2)

if multipage == '时间维度':
    # 侧边栏
    st.sidebar.header("请在这里筛选:")
    prodt_l5_up = st.sidebar.multiselect(
        "产品类型1:",
        options=df2["prodt_l5_up"].unique(),
        default=df2["prodt_l5_up"].unique()
    )
    prodt_l5 = st.sidebar.multiselect(
        "产品类型2:",
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
    st.info('本行 {} M1-M3整体情况'.format(prodt_l5_up))
    st.table(bh_select)
    bz_select = select_sjdf(df2, prodt_l5_up, prodt_l5, LOANSTATUS, group='第一组')
    st.info('本组 {} M1-M3整体情况'.format(prodt_l5_up))
    st.table(bz_select)
    qh_select = select_sjdf(df2, prodt_l5_up, prodt_l5, LOANSTATUS, group=None)
    st.info('全行 {} M1-M3整体情况'.format(prodt_l5_up))
    st.table(qh_select)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bh_select.index,
                             y=bh_select['M1-M3'],
                             mode='lines+markers',
                             name='本行'))
    fig.add_trace(go.Scatter(x=bz_select.index,
                             y=bz_select['M1-M3'],
                             mode='lines+markers',
                             name='本组'))
    fig.add_trace(go.Scatter(x=qh_select.index,
                             y=qh_select['M1-M3'],
                             mode='lines+markers',
                             name='全行'))
    fig.update_layout(width=800,
                      height=500,  # 改变整个figure的大小
                      title_text="产品 {} M1-M3".format(prodt_l5_up),
                      xaxis=dict(tickformat="%Y-%m")
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
    st.markdown('#### 报告区间 {} 至 {} 各产品M1-M3分析'.format(start_time, end_time))
    LOANSTATUS = st.sidebar.multiselect(
        "贷款状态:",
        options=df2["LOANSTATUS"].unique(),
        default=['FS01']
    )
    # 分隔符
    st.markdown("""---""")

    bh_select = select_cpdf(df1, start_time, end_time, prodt_select, LOANSTATUS, group=None)
    st.info('本行 {} 至 {} 各产品M1-M3整体情况'.format(start_time, end_time))
    st.table(bh_select)
    bz_select = select_cpdf(df2, start_time, end_time, prodt_select, LOANSTATUS, group='第一组')
    st.info('本组 {} 至 {} 各产品M1-M3整体情况'.format(start_time, end_time))
    st.table(bz_select)
    qh_select = select_cpdf(df2, start_time, end_time, prodt_select, LOANSTATUS, group=None)
    st.info('全行 {} 至 {} 各产品M1-M3整体情况'.format(start_time, end_time))
    st.table(qh_select)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=bh_select.index,
                         y=bh_select['M1-M3'],
                         name='本行'))
    fig.add_trace(go.Bar(x=bz_select.index,
                         y=bz_select['M1-M3'],
                         name='本组'))
    fig.add_trace(go.Bar(x=qh_select.index,
                         y=qh_select['M1-M3'],
                         name='全行'))
    fig.update_layout(width=800,
                      height=500,  # 改变整个figure的大小
                      title_text=' {} 至 {} 各产品M1-M3整体情况'.format(start_time, end_time),
                      xaxis=dict(tickformat="%Y-%m")
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
    index_select = st.sidebar.multiselect(
        "维度选择:",
        options=['sub_brh_name', 'prodt_l5_up', 'prodt_l5', 'prodt_l6_up'],
        default=['sub_brh_name', 'prodt_l5_up'],
    )

    st.markdown('#### 报告区间 {} 至 {} 各支行M1-M3分析'.format(start_time, end_time))
    bf_sysdata = select_bhdf(df1, start_time, end_time, LOANSTATUS, index_select)
